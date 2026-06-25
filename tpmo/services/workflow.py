"""
Workflow service — the state machine for the tPMO lifecycle.

Handles:
- Stage transitions based on human decisions
- Agent trigger dispatch to the correct CrewAI crew
- Audit logging
- Artefact persistence on the Initiative model
"""

import logging
import time
from decimal import Decimal

from django.utils import timezone

from tpmo.models import Initiative, InitiativeScore, AgentOutput, AuditLog, Decision

logger = logging.getLogger(__name__)

# Maps each stage to the crew runner function and artefact field to populate
STAGE_AGENT_MAP = {
    "intake": {
        "runner": "run_intake_triage",
        "artefact_field": "triage_output",
        "agent_name": "Intake & Triage Agent",
        "agent_role": "Technology PMO Intake Coordinator",
        "task_name": "intake_triage",
        "next_stage": "triage",
    },
    "triage": {
        "runner": None,  # triage uses same output as intake; human decision gate
        "artefact_field": None,
        "next_stage": "research",
    },
    "research": {
        "runner": "run_research_enrichment",
        "artefact_field": "research_output",
        "agent_name": "Research & Enrichment Agent",
        "agent_role": "Senior Business Analyst & Research Specialist",
        "task_name": "research_enrichment",
        "next_stage": "brief",
    },
    "brief": {
        "runner": "run_project_brief",
        "artefact_field": "project_brief",
        "agent_name": "Document Authoring Agent",
        "agent_role": "PMO Documentation Lead",
        "task_name": "project_brief",
        "next_stage": None,  # determined by size
    },
    "business_case": {
        "runner": "run_business_case",
        "artefact_field": "business_case",
        "agent_name": "Document Authoring Agent",
        "agent_role": "PMO Documentation Lead",
        "task_name": "business_case",
        "next_stage": "scoring",
    },
    "scoring": {
        "runner": "run_scoring",
        "artefact_field": "scoring_output",
        "agent_name": "Scoring & Prioritisation Agent",
        "agent_role": "Portfolio Strategy Analyst",
        "task_name": "scoring_prioritisation",
        "next_stage": "prc",
    },
    "prc": {
        "runner": "run_prc_pack",
        "artefact_field": "prc_pack",
        "agent_name": "Governance & Decision Support Agent",
        "agent_role": "PMO Governance Officer",
        "task_name": "prc_decision_pack",
        "next_stage": None,  # human terminal decision
    },
}


def _get_initiative_data(initiative: Initiative) -> dict:
    """Serialise an Initiative into a flat dict for agent consumption."""
    data = {
        "reference_code": initiative.reference_code,
        "title": initiative.title,
        "description": initiative.description,
        "submitter_name": initiative.submitter_name,
        "submitter_email": initiative.submitter_email,
        "department": initiative.get_department_display(),
        "business_sponsor": initiative.business_sponsor,
        "problem_statement": initiative.problem_statement,
        "expected_benefits": initiative.expected_benefits,
        "proposed_solution": initiative.proposed_solution,
        "strategic_alignment": initiative.strategic_alignment,
        "estimated_cost": str(initiative.estimated_cost) if initiative.estimated_cost else None,
        "estimated_duration_months": initiative.estimated_duration_months,
        "dependencies": initiative.dependencies,
        "constraints": initiative.constraints,
        "size": initiative.size,
        "stage": initiative.stage,
        # Include any existing artefacts for downstream agents
        "triage_output": initiative.triage_output,
        "research_output": initiative.research_output,
        "project_brief": initiative.project_brief,
        "business_case": initiative.business_case,
        "scoring_output": initiative.scoring_output,
    }
    return data


def trigger_agents(initiative: Initiative) -> dict:
    """
    Run the appropriate AI agent(s) for the initiative's current stage.
    Updates the initiative model with the agent output and advances state.
    Returns a result dict with success/error information.
    """
    from tpmo.services.agents import crew as crew_module

    stage = initiative.stage
    stage_config = STAGE_AGENT_MAP.get(stage)

    if not stage_config or not stage_config.get("runner"):
        return {"success": False, "error": f"No agent runner configured for stage: {stage}"}

    runner_name = stage_config["runner"]
    runner_fn = getattr(crew_module, runner_name, None)
    if not runner_fn:
        return {"success": False, "error": f"Runner function '{runner_name}' not found"}

    # Mark as processing
    initiative.ai_processing = True
    initiative.awaiting_decision = False
    initiative.save(update_fields=["ai_processing", "awaiting_decision"])

    _audit(initiative, "agent_triggered", f"agent:{stage_config['agent_name']}", {
        "stage": stage,
        "runner": runner_name,
    })

    try:
        t0 = time.time()
        initiative_data = _get_initiative_data(initiative)
        result = runner_fn(initiative_data)
        elapsed = time.time() - t0

        output = result.get("output", {})
        is_mock = result.get("is_mock", False)

        # Save structured output to the artefact field
        artefact_field = stage_config.get("artefact_field")
        if artefact_field and hasattr(initiative, artefact_field):
            setattr(initiative, artefact_field, output)

        # If this is the intake stage, also update size classification
        if stage == "intake":
            size = (output.get("classification") or {}).get("size", "")
            if size:
                initiative.size = size

        # Persist the score when scoring stage completes
        if stage == "scoring" and output:
            _persist_score(initiative, output)

        # Record agent output for audit trail
        AgentOutput.objects.create(
            initiative=initiative,
            agent_name=stage_config["agent_name"],
            agent_role=stage_config["agent_role"],
            task_name=stage_config["task_name"],
            stage=stage,
            input_summary=f"Initiative {initiative.reference_code} @ stage {stage}",
            structured_output=output,
            is_mock=is_mock,
            execution_seconds=elapsed,
        )

        # Advance to next stage
        next_stage = _determine_next_stage(initiative, stage)
        from_stage = initiative.stage
        initiative.stage = next_stage
        initiative.ai_processing = False
        initiative.awaiting_decision = True
        initiative.save()

        _audit(initiative, "agent_completed", f"agent:{stage_config['agent_name']}", {
            "from_stage": from_stage,
            "to_stage": next_stage,
            "is_mock": is_mock,
            "elapsed_seconds": round(elapsed, 2),
        })
        _audit(initiative, "stage_advanced", "system", {
            "from": from_stage,
            "to": next_stage,
        })

        return {"success": True, "stage": next_stage, "is_mock": is_mock}

    except Exception as exc:
        logger.exception("Agent execution failed for initiative %s", initiative.reference_code)
        initiative.ai_processing = False
        initiative.awaiting_decision = False
        initiative.save(update_fields=["ai_processing", "awaiting_decision"])
        return {"success": False, "error": str(exc)}


def _determine_next_stage(initiative: Initiative, current_stage: str) -> str:
    """State machine: return the next stage after AI processing completes."""
    if current_stage == "brief":
        # Medium/Large initiatives require a Business Case
        if initiative.size in ("medium", "large"):
            return "business_case"
        return "scoring"

    stage_config = STAGE_AGENT_MAP.get(current_stage, {})
    return stage_config.get("next_stage") or current_stage


def record_decision(
    initiative: Initiative,
    gate: str,
    decision: str,
    rationale: str,
    decided_by_name: str,
    conditions: str = "",
) -> Decision:
    """
    Record a human decision at a governance gate and advance the initiative stage.
    """
    dec = Decision.objects.create(
        initiative=initiative,
        gate=gate,
        decision=decision,
        decided_by_name=decided_by_name,
        rationale=rationale,
        conditions=conditions,
    )

    from_stage = initiative.stage
    _apply_decision(initiative, gate, decision)
    initiative.awaiting_decision = (decision == "request_info")
    initiative.save()

    _audit(initiative, "decision_recorded", decided_by_name, {
        "gate": gate,
        "decision": decision,
        "from_stage": from_stage,
        "to_stage": initiative.stage,
    })

    return dec


def _apply_decision(initiative: Initiative, gate: str, decision: str):
    """Mutate initiative stage based on human decision."""
    if decision == "reject":
        initiative.stage = "rejected"
    elif decision == "defer":
        initiative.stage = "deferred"
    elif decision == "approve":
        stage_after_approval = {
            "triage": "research",
            "brief_review": "business_case" if initiative.size in ("medium", "large") else "scoring",
            "bc_review": "scoring",
            "scoring_review": "prc",
            "prc": "backlog",
        }
        initiative.stage = stage_after_approval.get(gate, initiative.stage)
    # request_info and escalate leave stage unchanged


def _persist_score(initiative: Initiative, scoring_output: dict):
    """Create or update InitiativeScore from the scoring agent output."""
    ps = scoring_output.get("portfolio_strategy_score", {})
    sas = scoring_output.get("solution_attractiveness_score", {})
    roi = scoring_output.get("roi_analysis", {})

    score, _ = InitiativeScore.objects.get_or_create(initiative=initiative)
    score.strategic_alignment = ps.get("strategic_alignment", {}).get("score", 0)
    score.business_value = ps.get("business_value", {}).get("score", 0)
    score.urgency = ps.get("urgency", {}).get("score", 0)
    score.risk_inverse = ps.get("risk_inverse", {}).get("score", 0)
    score.feasibility = sas.get("feasibility", {}).get("score", 0)
    score.complexity_inverse = sas.get("complexity_inverse", {}).get("score", 0)
    score.resource_availability = sas.get("resource_availability", {}).get("score", 0)
    score.ps_score = Decimal(str(ps.get("weighted_total", 0)))
    score.sas_score = Decimal(str(sas.get("weighted_total", 0)))
    score.composite_score = Decimal(str(scoring_output.get("composite_score", 0)))
    score.roi_percentage = Decimal(str(roi.get("roi_percentage", 0) or 0))
    score.payback_months = roi.get("payback_months")
    score.npv = Decimal(str(roi.get("npv", 0) or 0))
    score.ai_recommendation = scoring_output.get("recommendation", "")
    score.scoring_rationale = scoring_output.get("scoring_rationale", "")
    score.save()


def _audit(initiative: Initiative, action: str, actor: str, details: dict):
    AuditLog.objects.create(
        initiative=initiative,
        action=action,
        actor=actor,
        from_stage=details.get("from", details.get("from_stage", "")),
        to_stage=details.get("to", details.get("to_stage", "")),
        details=details,
    )
