"""MCP client: spawns the LabSignal MCP server and keeps one stdio session open.

Slack's Bolt handlers are synchronous, but the MCP session and the Anthropic tool
loop are async and must outlive a single request. So we own one background thread
running one event loop, open the stdio session inside it once, and hand work to
that loop from the Slack threads.
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
import threading
from concurrent.futures import Future
from typing import Any, Coroutine

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

log = logging.getLogger(__name__)

STARTUP_TIMEOUT = 30.0


class MCPToolSession:
    """A live stdio session against `python -m labsignal.mcp_server`."""

    def __init__(self) -> None:
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="labsignal-mcp")
        self._started: Future[None] = Future()
        self._shutdown: asyncio.Event | None = None
        self.session: ClientSession | None = None
        self.tools: list[Any] = []

    def start(self) -> None:
        """Spawn the server and block until its tools have been discovered."""
        self._thread.start()
        self._started.result(timeout=STARTUP_TIMEOUT)
        log.info("MCP server exposes %d tools: %s", len(self.tools), self.tool_names())

    def tool_names(self) -> list[str]:
        return [tool.name for tool in self.tools]

    def run(self, coro: Coroutine[Any, Any, Any], timeout: float = 120.0) -> Any:
        """Run a coroutine on the MCP loop from a synchronous Slack handler."""
        return asyncio.run_coroutine_threadsafe(coro, self._loop).result(timeout=timeout)

    def stop(self) -> None:
        if self._shutdown is not None:
            self._loop.call_soon_threadsafe(self._shutdown.set)
        self._thread.join(timeout=10)

    # -- internals ---------------------------------------------------------

    def _run_loop(self) -> None:
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._serve())
        except Exception as error:  # surfaced to start() via the future
            if not self._started.done():
                self._started.set_exception(error)
            else:
                log.exception("MCP session ended unexpectedly")
        finally:
            self._loop.close()

    async def _serve(self) -> None:
        self._shutdown = asyncio.Event()
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "labsignal.mcp_server"],
            # The server needs SLACK_BOT_TOKEN to serve read_slack_channel, and
            # PYTHONPATH so `-m labsignal.mcp_server` resolves from a source checkout.
            env={**os.environ, "PYTHONPATH": _src_root()},
        )
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                self.session = session
                self.tools = (await session.list_tools()).tools
                self._started.set_result(None)
                # Hold both context managers open for the life of the process.
                await self._shutdown.wait()


def _src_root() -> str:
    package_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(package_dir)
