from rest_framework import serializers
from tpmo.models import Initiative, InitiativeScore, Decision, AgentOutput, AuditLog


class InitiativeScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = InitiativeScore
        exclude = ("initiative",)


class DecisionSerializer(serializers.ModelSerializer):
    gate_display = serializers.CharField(source="get_gate_display", read_only=True)
    decision_display = serializers.CharField(source="get_decision_display", read_only=True)

    class Meta:
        model = Decision
        fields = "__all__"
        read_only_fields = ("id", "decided_at", "decided_by")


class AgentOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentOutput
        fields = "__all__"
        read_only_fields = ("id", "created_at")


class AuditLogSerializer(serializers.ModelSerializer):
    action_display = serializers.CharField(source="get_action_display", read_only=True)

    class Meta:
        model = AuditLog
        fields = "__all__"
        read_only_fields = ("id", "timestamp")


class InitiativeListSerializer(serializers.ModelSerializer):
    stage_display = serializers.CharField(source="get_stage_display", read_only=True)
    size_display = serializers.CharField(source="get_size_display", read_only=True)
    department_display = serializers.CharField(source="get_department_display", read_only=True)
    composite_score = serializers.SerializerMethodField()

    class Meta:
        model = Initiative
        fields = (
            "id", "reference_code", "title", "department", "department_display",
            "stage", "stage_display", "size", "size_display", "ai_processing",
            "awaiting_decision", "estimated_cost", "created_at", "composite_score",
        )

    def get_composite_score(self, obj):
        try:
            return float(obj.score.composite_score)
        except Exception:
            return None


class InitiativeDetailSerializer(serializers.ModelSerializer):
    stage_display = serializers.CharField(source="get_stage_display", read_only=True)
    size_display = serializers.CharField(source="get_size_display", read_only=True)
    department_display = serializers.CharField(source="get_department_display", read_only=True)
    score = InitiativeScoreSerializer(read_only=True)
    decisions = DecisionSerializer(many=True, read_only=True)
    agent_outputs = AgentOutputSerializer(many=True, read_only=True)
    audit_logs = AuditLogSerializer(many=True, read_only=True)

    class Meta:
        model = Initiative
        fields = "__all__"


class InitiativeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Initiative
        fields = (
            "title", "description", "submitter_name", "submitter_email",
            "department", "business_sponsor", "problem_statement",
            "expected_benefits", "proposed_solution", "strategic_alignment",
            "estimated_cost", "estimated_duration_months", "target_go_live",
            "dependencies", "constraints",
        )
