import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Initiative(models.Model):
    STAGE_CHOICES = [
        ("intake", "Intake"),
        ("triage", "Triage & Deduplication"),
        ("research", "Research & Enrichment"),
        ("brief", "Project Brief"),
        ("business_case", "Business Case"),
        ("scoring", "Scoring & Prioritisation"),
        ("prc", "PRC Decision"),
        ("backlog", "Approved Backlog"),
        ("rejected", "Rejected"),
        ("deferred", "Deferred"),
        ("duplicate", "Duplicate"),
    ]

    SIZE_CHOICES = [
        ("small", "Small  (<$50K)"),
        ("medium", "Medium ($50K–$500K)"),
        ("large", "Large  (>$500K)"),
    ]

    DEPARTMENT_CHOICES = [
        ("finance", "Finance"),
        ("operations", "Operations"),
        ("technology", "Technology"),
        ("hr", "Human Resources"),
        ("sales", "Sales & Marketing"),
        ("legal", "Legal & Compliance"),
        ("other", "Other"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference_code = models.CharField(max_length=20, unique=True, blank=True)

    # Submitter info
    title = models.CharField(max_length=255)
    description = models.TextField()
    submitter_name = models.CharField(max_length=100)
    submitter_email = models.EmailField()
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, default="technology")
    business_sponsor = models.CharField(max_length=100, blank=True)

    # Business context
    problem_statement = models.TextField(blank=True)
    expected_benefits = models.TextField(blank=True)
    proposed_solution = models.TextField(blank=True)
    strategic_alignment = models.TextField(blank=True)
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    estimated_duration_months = models.IntegerField(null=True, blank=True)
    target_go_live = models.DateField(null=True, blank=True)
    dependencies = models.TextField(blank=True)
    constraints = models.TextField(blank=True)

    # Lifecycle state
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default="intake")
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, blank=True)
    ai_processing = models.BooleanField(default=False)
    awaiting_decision = models.BooleanField(default=False)

    # Deduplication
    duplicate_of = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="duplicates",
    )

    # AI-generated artefacts (structured JSON per agent stage)
    triage_output = models.JSONField(null=True, blank=True)
    research_output = models.JSONField(null=True, blank=True)
    project_brief = models.JSONField(null=True, blank=True)
    business_case = models.JSONField(null=True, blank=True)
    scoring_output = models.JSONField(null=True, blank=True)
    prc_pack = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.reference_code}] {self.title}"

    def save(self, *args, **kwargs):
        if not self.reference_code:
            year = timezone.now().year
            count = Initiative.objects.count() + 1
            self.reference_code = f"TPMO-{year}-{count:04d}"
        super().save(*args, **kwargs)

    @property
    def stage_display(self):
        return dict(self.STAGE_CHOICES).get(self.stage, self.stage)

    @property
    def can_run_agents(self):
        terminal = {"backlog", "rejected", "deferred", "duplicate"}
        return not self.ai_processing and self.stage not in terminal

    @property
    def next_gate(self):
        """Return the human-decision gate key for the current stage."""
        gate_map = {
            "triage": "triage",
            "brief": "brief_review",
            "business_case": "bc_review",
            "scoring": "scoring_review",
            "prc": "prc",
        }
        return gate_map.get(self.stage)


class InitiativeScore(models.Model):
    initiative = models.OneToOneField(Initiative, on_delete=models.CASCADE, related_name="score")

    # Portfolio Strategy Score (PS) – 1–5 each
    strategic_alignment = models.IntegerField(default=0)
    business_value = models.IntegerField(default=0)
    urgency = models.IntegerField(default=0)
    risk_inverse = models.IntegerField(default=0)  # higher = lower risk

    # Solution Attractiveness Score (SAS) – 1–5 each
    feasibility = models.IntegerField(default=0)
    complexity_inverse = models.IntegerField(default=0)  # higher = lower complexity
    resource_availability = models.IntegerField(default=0)

    # ROI
    roi_percentage = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    payback_months = models.IntegerField(null=True, blank=True)
    npv = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    # Composites
    ps_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sas_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    composite_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    priority_rank = models.IntegerField(null=True, blank=True)

    ai_recommendation = models.TextField(blank=True)
    scoring_rationale = models.TextField(blank=True)
    scored_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Score {self.composite_score} — {self.initiative.reference_code}"


class Decision(models.Model):
    DECISION_CHOICES = [
        ("approve", "Approve"),
        ("reject", "Reject"),
        ("defer", "Defer"),
        ("request_info", "Request More Information"),
        ("escalate", "Escalate"),
    ]

    GATE_CHOICES = [
        ("triage", "Triage Gate"),
        ("brief_review", "Brief Review Gate"),
        ("bc_review", "Business Case Review Gate"),
        ("scoring_review", "Scoring Review Gate"),
        ("prc", "PRC Decision Gate"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    initiative = models.ForeignKey(Initiative, on_delete=models.CASCADE, related_name="decisions")
    gate = models.CharField(max_length=30, choices=GATE_CHOICES)
    decision = models.CharField(max_length=20, choices=DECISION_CHOICES)
    decided_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    decided_by_name = models.CharField(max_length=100, blank=True)
    rationale = models.TextField()
    conditions = models.TextField(blank=True)
    next_review_date = models.DateField(null=True, blank=True)
    decided_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-decided_at"]

    def __str__(self):
        return f"{self.get_gate_display()} → {self.get_decision_display()} [{self.initiative.reference_code}]"


class AgentOutput(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    initiative = models.ForeignKey(Initiative, on_delete=models.CASCADE, related_name="agent_outputs")
    agent_name = models.CharField(max_length=100)
    agent_role = models.CharField(max_length=150)
    task_name = models.CharField(max_length=100)
    stage = models.CharField(max_length=20)
    input_summary = models.TextField(blank=True)
    raw_output = models.TextField(blank=True)
    structured_output = models.JSONField(null=True, blank=True)
    is_mock = models.BooleanField(default=False)
    execution_seconds = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.agent_name} @ {self.stage} [{self.initiative.reference_code}]"


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("submitted", "Initiative Submitted"),
        ("stage_advanced", "Stage Advanced"),
        ("agent_triggered", "Agent Triggered"),
        ("agent_completed", "Agent Completed"),
        ("decision_recorded", "Decision Recorded"),
        ("artefact_updated", "Artefact Updated"),
        ("status_changed", "Status Changed"),
    ]

    initiative = models.ForeignKey(Initiative, on_delete=models.CASCADE, related_name="audit_logs")
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    actor = models.CharField(max_length=100)  # 'system', 'agent:<Name>', or username
    from_stage = models.CharField(max_length=20, blank=True)
    to_stage = models.CharField(max_length=20, blank=True)
    details = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.action} on {self.initiative.reference_code} by {self.actor}"
