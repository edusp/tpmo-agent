from django.contrib import admin
from django.utils.html import format_html
from .models import Initiative, InitiativeScore, Decision, AgentOutput, AuditLog


class InitiativeScoreInline(admin.StackedInline):
    model = InitiativeScore
    extra = 0
    readonly_fields = ("scored_at",)


class DecisionInline(admin.TabularInline):
    model = Decision
    extra = 0
    readonly_fields = ("decided_at",)
    fields = ("gate", "decision", "decided_by_name", "rationale", "decided_at")


class AuditLogInline(admin.TabularInline):
    model = AuditLog
    extra = 0
    readonly_fields = ("action", "actor", "from_stage", "to_stage", "timestamp")
    fields = ("action", "actor", "from_stage", "to_stage", "timestamp")
    can_delete = False


@admin.register(Initiative)
class InitiativeAdmin(admin.ModelAdmin):
    list_display = (
        "reference_code", "title", "department", "stage_badge",
        "size", "ai_processing", "awaiting_decision", "created_at"
    )
    list_filter = ("stage", "size", "department", "ai_processing", "awaiting_decision")
    search_fields = ("reference_code", "title", "submitter_name", "submitter_email")
    readonly_fields = ("id", "reference_code", "created_at", "updated_at")
    inlines = [InitiativeScoreInline, DecisionInline, AuditLogInline]

    fieldsets = (
        ("Identity", {
            "fields": ("id", "reference_code", "title", "description")
        }),
        ("Submitter", {
            "fields": ("submitter_name", "submitter_email", "department", "business_sponsor")
        }),
        ("Business Context", {
            "fields": (
                "problem_statement", "expected_benefits", "proposed_solution",
                "strategic_alignment", "estimated_cost", "estimated_duration_months",
                "target_go_live", "dependencies", "constraints",
            )
        }),
        ("Lifecycle", {
            "fields": ("stage", "size", "ai_processing", "awaiting_decision", "duplicate_of")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    def stage_badge(self, obj):
        colours = {
            "intake": "gray", "triage": "blue", "research": "purple",
            "brief": "orange", "business_case": "orange", "scoring": "teal",
            "prc": "indigo", "backlog": "green", "rejected": "red",
            "deferred": "yellow", "duplicate": "gray",
        }
        colour = colours.get(obj.stage, "gray")
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 6px;border-radius:4px">{}</span>',
            colour, obj.get_stage_display()
        )
    stage_badge.short_description = "Stage"


@admin.register(InitiativeScore)
class InitiativeScoreAdmin(admin.ModelAdmin):
    list_display = ("initiative", "composite_score", "ps_score", "sas_score", "priority_rank", "scored_at")
    readonly_fields = ("scored_at",)


@admin.register(Decision)
class DecisionAdmin(admin.ModelAdmin):
    list_display = ("initiative", "gate", "decision", "decided_by_name", "decided_at")
    list_filter = ("gate", "decision")
    search_fields = ("initiative__reference_code", "decided_by_name")


@admin.register(AgentOutput)
class AgentOutputAdmin(admin.ModelAdmin):
    list_display = ("initiative", "agent_name", "stage", "is_mock", "execution_seconds", "created_at")
    list_filter = ("agent_name", "stage", "is_mock")
    search_fields = ("initiative__reference_code", "agent_name")
    readonly_fields = ("created_at",)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("initiative", "action", "actor", "from_stage", "to_stage", "timestamp")
    list_filter = ("action",)
    search_fields = ("initiative__reference_code", "actor")
    readonly_fields = ("timestamp",)
