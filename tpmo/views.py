from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone

from .models import Initiative, Decision, AuditLog
from .services import workflow


# ---------------------------------------------------------------------------
# Dashboard / Funnel View
# ---------------------------------------------------------------------------

STAGE_ORDER = [
    "intake", "triage", "research", "brief",
    "business_case", "scoring", "prc", "backlog",
    "rejected", "deferred", "duplicate",
]


def dashboard(request):
    initiatives = Initiative.objects.select_related("score").all()

    # Filter
    stage_filter = request.GET.get("stage", "")
    search = request.GET.get("search", "")
    if stage_filter:
        initiatives = initiatives.filter(stage=stage_filter)
    if search:
        initiatives = initiatives.filter(
            Q(title__icontains=search) | Q(reference_code__icontains=search)
        )

    # KPI cards
    total = Initiative.objects.count()
    awaiting = Initiative.objects.filter(awaiting_decision=True).count()
    processing = Initiative.objects.filter(ai_processing=True).count()
    approved = Initiative.objects.filter(stage="backlog").count()

    # Stage breakdown for funnel
    stage_counts = {
        s: Initiative.objects.filter(stage=s).count()
        for s in STAGE_ORDER
    }

    stage_data = [
        {"key": k, "label": l, "count": stage_counts.get(k, 0)}
        for k, l in Initiative.STAGE_CHOICES
    ]

    return render(request, "tpmo/dashboard.html", {
        "initiatives": initiatives,
        "stage_filter": stage_filter,
        "search": search,
        "total": total,
        "awaiting": awaiting,
        "processing": processing,
        "approved": approved,
        "stage_counts": stage_counts,
        "stage_choices": Initiative.STAGE_CHOICES,
        "stage_data": stage_data,
    })


# ---------------------------------------------------------------------------
# Intake Form
# ---------------------------------------------------------------------------

def intake(request):
    if request.method == "POST":
        data = request.POST

        # Basic validation
        required = ["title", "description", "submitter_name", "submitter_email", "department"]
        errors = {f: f"{f.replace('_', ' ').title()} is required" for f in required if not data.get(f)}
        if errors:
            return render(request, "tpmo/intake.html", {
                "errors": errors,
                "data": data,
                "department_choices": Initiative.DEPARTMENT_CHOICES,
            })

        initiative = Initiative.objects.create(
            title=data["title"],
            description=data["description"],
            submitter_name=data["submitter_name"],
            submitter_email=data["submitter_email"],
            department=data["department"],
            business_sponsor=data.get("business_sponsor", ""),
            problem_statement=data.get("problem_statement", ""),
            expected_benefits=data.get("expected_benefits", ""),
            proposed_solution=data.get("proposed_solution", ""),
            strategic_alignment=data.get("strategic_alignment", ""),
            estimated_cost=data.get("estimated_cost") or None,
            estimated_duration_months=data.get("estimated_duration_months") or None,
            dependencies=data.get("dependencies", ""),
            constraints=data.get("constraints", ""),
            stage="intake",
            ai_processing=False,
            awaiting_decision=False,
        )

        AuditLog.objects.create(
            initiative=initiative,
            action="submitted",
            actor=data["submitter_name"],
            details={"submitter_email": data["submitter_email"]},
        )

        messages.success(request, f"Initiative {initiative.reference_code} submitted. Running AI intake analysis...")

        # Trigger intake agent immediately (mock: instant)
        result = workflow.trigger_agents(initiative)
        if result.get("success"):
            messages.info(request, f"AI analysis complete. Initiative is now at stage: {initiative.stage}")
        else:
            messages.warning(request, f"AI analysis encountered an issue: {result.get('error')}")

        return redirect("initiative-detail", pk=initiative.pk)

    return render(request, "tpmo/intake.html", {
        "department_choices": Initiative.DEPARTMENT_CHOICES,
        "data": {},
        "errors": {},
    })


# ---------------------------------------------------------------------------
# Initiative Detail
# ---------------------------------------------------------------------------

def initiative_detail(request, pk):
    initiative = get_object_or_404(
        Initiative.objects.prefetch_related(
            "decisions", "agent_outputs", "audit_logs", "score"
        ),
        pk=pk
    )

    # Handle agent trigger
    if request.method == "POST" and request.POST.get("action") == "trigger_agents":
        if initiative.can_run_agents:
            result = workflow.trigger_agents(initiative)
            if result.get("success"):
                messages.success(request, f"AI agents completed. Stage advanced to: {initiative.stage}")
            else:
                messages.error(request, f"Agent error: {result.get('error')}")
        else:
            messages.warning(request, "Cannot run agents at this stage.")
        return redirect("initiative-detail", pk=pk)

    return render(request, "tpmo/initiative_detail.html", {
        "initiative": initiative,
        "gate_choices": Decision.GATE_CHOICES,
        "decision_choices": Decision.DECISION_CHOICES,
        "stage_choices": Initiative.STAGE_CHOICES,
    })


# ---------------------------------------------------------------------------
# Decision Recording (called from initiative detail form)
# ---------------------------------------------------------------------------

def record_decision(request, pk):
    initiative = get_object_or_404(Initiative, pk=pk)

    if request.method == "POST":
        gate = request.POST.get("gate")
        decision_value = request.POST.get("decision")
        rationale = request.POST.get("rationale", "")
        decided_by_name = request.POST.get("decided_by_name", "PMO Reviewer")
        conditions = request.POST.get("conditions", "")

        if not gate or not decision_value or not rationale:
            messages.error(request, "Gate, decision, and rationale are all required.")
            return redirect("initiative-detail", pk=pk)

        workflow.record_decision(
            initiative=initiative,
            gate=gate,
            decision=decision_value,
            rationale=rationale,
            decided_by_name=decided_by_name,
            conditions=conditions,
        )

        label = dict(Decision.DECISION_CHOICES).get(decision_value, decision_value)
        messages.success(request, f"Decision recorded: {label}. Initiative is now at stage: {initiative.stage}.")

        # If approved and next stage needs agents, auto-trigger
        if decision_value == "approve" and initiative.can_run_agents:
            result = workflow.trigger_agents(initiative)
            if result.get("success"):
                messages.info(request, f"AI agents triggered automatically. Stage: {initiative.stage}")

    return redirect("initiative-detail", pk=pk)


# ---------------------------------------------------------------------------
# PRC Decision Screen
# ---------------------------------------------------------------------------

def prc_decision(request, pk):
    initiative = get_object_or_404(
        Initiative.objects.prefetch_related("decisions", "score"),
        pk=pk
    )

    if initiative.stage != "prc":
        messages.warning(request, f"This initiative is at stage '{initiative.stage}', not 'prc'.")

    if request.method == "POST":
        decision_value = request.POST.get("decision")
        rationale = request.POST.get("rationale", "")
        decided_by_name = request.POST.get("decided_by_name", "PRC Chair")
        conditions = request.POST.get("conditions", "")

        if not decision_value or not rationale:
            messages.error(request, "Decision and rationale are required.")
            return render(request, "tpmo/prc_decision.html", {"initiative": initiative})

        workflow.record_decision(
            initiative=initiative,
            gate="prc",
            decision=decision_value,
            rationale=rationale,
            decided_by_name=decided_by_name,
            conditions=conditions,
        )

        label = dict(Decision.DECISION_CHOICES).get(decision_value, decision_value)
        messages.success(request, f"PRC decision recorded: {label}. Initiative stage: {initiative.stage}.")
        return redirect("initiative-detail", pk=pk)

    return render(request, "tpmo/prc_decision.html", {
        "initiative": initiative,
        "decision_choices": [
            ("approve", "Approve"),
            ("reject", "Reject"),
            ("defer", "Defer"),
        ],
    })
