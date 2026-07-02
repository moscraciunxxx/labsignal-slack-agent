"""Deterministic tools exposed to Slack and MCP."""

from __future__ import annotations

import re

from .knowledge import find_experiment_plan, search_protocols


def extract_action_items(text: str) -> list[dict[str, str]]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    items: list[dict[str, str]] = []
    cue = re.compile(r"\b(will|should|needs to|need to|by|before|todo|action)\b", re.I)
    owner_re = re.compile(r"\b([A-Z][a-z]+)\b")
    date_re = re.compile(r"\b(today|tomorrow|friday|monday|tuesday|wednesday|thursday|next week|\d{1,2}/\d{1,2})\b", re.I)
    for sentence in sentences:
        if not sentence or not cue.search(sentence):
            continue
        owner = owner_re.search(sentence)
        deadline = date_re.search(sentence)
        items.append(
            {
                "owner": owner.group(1) if owner else "unassigned",
                "task": sentence.strip(),
                "deadline": deadline.group(1) if deadline else "not specified",
            }
        )
    return items


def summarize_update(text: str) -> str:
    compact = " ".join(text.split())
    if len(compact) <= 260:
        return compact
    first = re.split(r"(?<=[.!?])\s+", compact)[0]
    return first[:260].strip()


def detect_risks(text: str) -> list[dict[str, str]]:
    checks = [
        (
            "Signal quality",
            r"\b(saturated|flatline|noisy|artifact|drift|motion|high[- ]variance)\b",
            "Review QC before downstream analysis.",
        ),
        (
            "Missing owner",
            r"\b(todo|needs to|should|action)\b(?!.*\b[A-Z][a-z]+\b)",
            "Assign an explicit owner.",
        ),
        (
            "Schedule risk",
            r"\b(delayed|blocked|waiting|late|missed|re-run|rerun)\b",
            "Decide whether the session needs escalation or re-planning.",
        ),
        (
            "Data governance",
            r"\b(consent|human|patient|privacy|de-identify|restricted)\b",
            "Confirm sharing and de-identification constraints.",
        ),
        (
            "Reproducibility",
            r"\b(manual|spreadsheet|local path|notebook only|unversioned)\b",
            "Capture scripts, parameters, and environment details.",
        ),
    ]
    risks: list[dict[str, str]] = []
    for label, pattern, mitigation in checks:
        if re.search(pattern, text, flags=re.I):
            risks.append({"risk": label, "mitigation": mitigation})
    return risks


def build_research_brief(text: str) -> dict[str, object]:
    protocols = search_protocols(text, limit=2)
    return {
        "summary": summarize_update(text),
        "actions": extract_action_items(text),
        "risks": detect_risks(text),
        "protocols": protocols,
    }


def plan_experiment(query: str) -> dict[str, object]:
    plan = find_experiment_plan(query)
    if plan is None:
        return {
            "id": "general-research-handoff",
            "title": "General research handoff checklist",
            "steps": [
                "State the scientific question and current decision point.",
                "List dataset/session IDs and quality concerns.",
                "Assign owners and deadlines for next actions.",
                "Link relevant protocol or SOP context.",
                "Record unresolved risks before work continues.",
            ],
        }
    return plan


def format_actions(items: list[dict[str, str]]) -> str:
    if not items:
        return "No clear action items found. Try including an owner, task, and deadline."
    lines = ["*Action items*"]
    for item in items:
        lines.append(f"- *{item['owner']}*: {item['task']} _Deadline: {item['deadline']}._")
    return "\n".join(lines)


def format_protocols(results: list[dict[str, str]]) -> str:
    if not results:
        return "I could not find a matching protocol in the local knowledge base."
    lines = ["*Protocol matches*"]
    for result in results:
        lines.append(f"- *{result['title']}* `({result['id']})`: {result['body']}")
    return "\n".join(lines)


def format_risks(risks: list[dict[str, str]]) -> str:
    if not risks:
        return "*Risks*\n- No obvious QC, schedule, governance, or reproducibility risks detected."
    lines = ["*Risks and mitigations*"]
    for item in risks:
        lines.append(f"- *{item['risk']}*: {item['mitigation']}")
    return "\n".join(lines)


def format_plan(plan: dict[str, object]) -> str:
    lines = [f"*{plan['title']}*"]
    for idx, step in enumerate(plan["steps"], start=1):
        lines.append(f"{idx}. {step}")
    return "\n".join(lines)


def format_research_brief(brief: dict[str, object]) -> str:
    lines = ["*LabSignal research brief*", f"*Summary:* {brief['summary']}"]

    actions = brief["actions"]
    if actions:
        lines.append("*Action items*")
        for item in actions:
            lines.append(f"- *{item['owner']}*: {item['task']} _Deadline: {item['deadline']}._")
    else:
        lines.append("*Action items*\n- No clear owner/task/deadline pairs found.")

    risks = brief["risks"]
    if risks:
        lines.append("*Risks*")
        for item in risks:
            lines.append(f"- *{item['risk']}*: {item['mitigation']}")
    else:
        lines.append("*Risks*\n- No obvious blockers detected.")

    protocols = brief["protocols"]
    if protocols:
        lines.append("*Relevant protocols*")
        for result in protocols:
            lines.append(f"- *{result['title']}* `({result['id']})`")
    return "\n".join(lines)
