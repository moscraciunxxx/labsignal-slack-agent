from labsignal import LabSignalAgent
from labsignal.knowledge import search_protocols
from labsignal.tools import build_research_brief, detect_risks, extract_action_items, plan_experiment


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


def test_risk_detection():
    risks = detect_risks("Two CA1 channels are saturated and the session needs a re-run.")
    labels = {item["risk"] for item in risks}
    assert "Signal quality" in labels
    assert "Schedule risk" in labels


def test_research_brief_combines_tools():
    brief = build_research_brief(
        "Alice will QC CA1 Neuropixels recordings by Friday. Two channels are saturated."
    )
    assert brief["summary"]
    assert brief["actions"]
    assert brief["risks"]
    assert brief["protocols"]


def test_plan_experiment_matches_ca1():
    plan = plan_experiment("ca1 neuropixels qc")
    assert plan["id"] == "ca1-neuropixels"
    assert len(plan["steps"]) >= 3


def test_agent_brief_response():
    response = LabSignalAgent().respond(
        "brief Alice will QC CA1 Neuropixels recordings by Friday. Two channels are saturated."
    )
    assert "LabSignal research brief" in response
    assert "Risks" in response


def test_agent_plan_response():
    response = LabSignalAgent().respond("plan ca1 neuropixels qc")
    assert "CA1 Neuropixels" in response
