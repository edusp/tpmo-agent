"""
Crew orchestrator for the tPMO system.

When TPMO_MOCK_AGENTS=True (or no OPENAI_API_KEY is set), runs instantly
with realistic mock data. When a real LLM key is present, uses CrewAI
with the configured model.
"""

import json
import time
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def _use_mock() -> bool:
    import os
    if getattr(settings, "TPMO_MOCK_AGENTS", True):
        return True
    api_key = os.environ.get("OPENAI_API_KEY", "")
    return not bool(api_key)


def run_intake_triage(initiative_data: dict) -> dict:
    if _use_mock():
        from .mock_outputs import get_mock_triage_output
        return {"output": get_mock_triage_output(initiative_data), "is_mock": True}

    from crewai import Crew, Process
    from .agents import build_intake_triage_agent
    from .tasks import build_intake_triage_task

    agent = build_intake_triage_agent()
    task = build_intake_triage_task(agent, initiative_data)
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)

    t0 = time.time()
    result = crew.kickoff(inputs=initiative_data)
    elapsed = time.time() - t0

    raw = str(result)
    try:
        structured = json.loads(raw)
    except json.JSONDecodeError:
        structured = {"raw_text": raw}

    return {"output": structured, "is_mock": False, "elapsed": elapsed}


def run_research_enrichment(initiative_data: dict) -> dict:
    if _use_mock():
        from .mock_outputs import get_mock_research_output
        return {"output": get_mock_research_output(initiative_data), "is_mock": True}

    from crewai import Crew, Process
    from .agents import build_research_enrichment_agent
    from .tasks import build_research_enrichment_task

    agent = build_research_enrichment_agent()
    task = build_research_enrichment_task(agent, initiative_data)
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)

    t0 = time.time()
    result = crew.kickoff(inputs=initiative_data)
    elapsed = time.time() - t0

    raw = str(result)
    try:
        structured = json.loads(raw)
    except json.JSONDecodeError:
        structured = {"raw_text": raw}

    return {"output": structured, "is_mock": False, "elapsed": elapsed}


def run_project_brief(initiative_data: dict) -> dict:
    if _use_mock():
        from .mock_outputs import get_mock_project_brief
        return {"output": get_mock_project_brief(initiative_data), "is_mock": True}

    from crewai import Crew, Process
    from .agents import build_document_authoring_agent
    from .tasks import build_project_brief_task

    agent = build_document_authoring_agent()
    task = build_project_brief_task(agent, initiative_data)
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)

    t0 = time.time()
    result = crew.kickoff(inputs=initiative_data)
    elapsed = time.time() - t0

    raw = str(result)
    try:
        structured = json.loads(raw)
    except json.JSONDecodeError:
        structured = {"raw_text": raw}

    return {"output": structured, "is_mock": False, "elapsed": elapsed}


def run_business_case(initiative_data: dict) -> dict:
    if _use_mock():
        from .mock_outputs import get_mock_business_case
        return {"output": get_mock_business_case(initiative_data), "is_mock": True}

    from crewai import Crew, Process
    from .agents import build_document_authoring_agent
    from .tasks import build_business_case_task

    agent = build_document_authoring_agent()
    task = build_business_case_task(agent, initiative_data)
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)

    t0 = time.time()
    result = crew.kickoff(inputs=initiative_data)
    elapsed = time.time() - t0

    raw = str(result)
    try:
        structured = json.loads(raw)
    except json.JSONDecodeError:
        structured = {"raw_text": raw}

    return {"output": structured, "is_mock": False, "elapsed": elapsed}


def run_scoring(initiative_data: dict) -> dict:
    if _use_mock():
        from .mock_outputs import get_mock_scoring_output
        return {"output": get_mock_scoring_output(initiative_data), "is_mock": True}

    from crewai import Crew, Process
    from .agents import build_scoring_prioritisation_agent
    from .tasks import build_scoring_task

    agent = build_scoring_prioritisation_agent()
    task = build_scoring_task(agent, initiative_data)
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)

    t0 = time.time()
    result = crew.kickoff(inputs=initiative_data)
    elapsed = time.time() - t0

    raw = str(result)
    try:
        structured = json.loads(raw)
    except json.JSONDecodeError:
        structured = {"raw_text": raw}

    return {"output": structured, "is_mock": False, "elapsed": elapsed}


def run_prc_pack(initiative_data: dict) -> dict:
    if _use_mock():
        from .mock_outputs import get_mock_prc_pack
        return {"output": get_mock_prc_pack(initiative_data), "is_mock": True}

    from crewai import Crew, Process
    from .agents import build_governance_decision_support_agent
    from .tasks import build_prc_pack_task

    agent = build_governance_decision_support_agent()
    task = build_prc_pack_task(agent, initiative_data)
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)

    t0 = time.time()
    result = crew.kickoff(inputs=initiative_data)
    elapsed = time.time() - t0

    raw = str(result)
    try:
        structured = json.loads(raw)
    except json.JSONDecodeError:
        structured = {"raw_text": raw}

    return {"output": structured, "is_mock": False, "elapsed": elapsed}
