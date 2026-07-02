from labsignal import LabSignalAgent
from labsignal.knowledge import search_protocols
from labsignal.tools import extract_action_items


def test_extract_action_items():
    items = extract_action_items("Alice will QC CA1 recordings by Friday. Bob should update the SOP.")
    assert len(items) == 2
    assert items[0]["owner"] == "Alice"
    assert items[0]["deadline"].lower() == "friday"


def test_protocol_search():
    results = search_protocols("ca1 neuropixels qc")
    assert results
    assert results[0]["id"] == "ca1-neuropixels-qc"


def test_agent_actions_response():
    response = LabSignalAgent().respond("actions Alice will QC CA1 recordings by Friday.")
    assert "Action items" in response
    assert "Alice" in response


def test_agent_help_response():
    response = LabSignalAgent().respond("hello")
    assert "actions" in response
    assert "protocol" in response

