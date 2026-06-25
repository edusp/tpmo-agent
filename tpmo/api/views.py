from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Q

from tpmo.models import Initiative, InitiativeScore
from tpmo.services import workflow
from .serializers import (
    InitiativeListSerializer,
    InitiativeDetailSerializer,
    InitiativeCreateSerializer,
    DecisionSerializer,
    InitiativeScoreSerializer,
)


class InitiativeListCreateView(generics.ListCreateAPIView):
    queryset = Initiative.objects.select_related("score").all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return InitiativeCreateSerializer
        return InitiativeListSerializer

    def perform_create(self, serializer):
        initiative = serializer.save(stage="intake", awaiting_decision=False, ai_processing=True)
        # Auto-trigger intake agent after creation
        workflow.trigger_agents(initiative)


class InitiativeDetailView(generics.RetrieveUpdateAPIView):
    queryset = Initiative.objects.prefetch_related(
        "score", "decisions", "agent_outputs", "audit_logs"
    ).all()
    serializer_class = InitiativeDetailSerializer


class TriggerAgentView(APIView):
    """POST to manually trigger AI agents for the current stage."""

    def post(self, request, pk):
        try:
            initiative = Initiative.objects.get(pk=pk)
        except Initiative.DoesNotExist:
            return Response({"error": "Initiative not found"}, status=status.HTTP_404_NOT_FOUND)

        if not initiative.can_run_agents:
            return Response(
                {"error": "Cannot trigger agents: initiative is in a terminal stage or already processing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = workflow.trigger_agents(initiative)

        if result.get("success"):
            return Response({
                "success": True,
                "stage": result.get("stage"),
                "is_mock": result.get("is_mock"),
                "message": f"Agents completed. Initiative advanced to stage: {result.get('stage')}",
            })
        return Response({"success": False, "error": result.get("error")}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RecordDecisionView(APIView):
    """POST to record a human governance decision at a gate."""

    def post(self, request, pk):
        try:
            initiative = Initiative.objects.get(pk=pk)
        except Initiative.DoesNotExist:
            return Response({"error": "Initiative not found"}, status=status.HTTP_404_NOT_FOUND)

        gate = request.data.get("gate")
        decision = request.data.get("decision")
        rationale = request.data.get("rationale", "")
        decided_by_name = request.data.get("decided_by_name", "Anonymous")
        conditions = request.data.get("conditions", "")

        if not gate or not decision:
            return Response({"error": "gate and decision are required"}, status=status.HTTP_400_BAD_REQUEST)

        dec = workflow.record_decision(
            initiative=initiative,
            gate=gate,
            decision=decision,
            rationale=rationale,
            decided_by_name=decided_by_name,
            conditions=conditions,
        )

        return Response({
            "success": True,
            "decision_id": str(dec.id),
            "new_stage": initiative.stage,
            "message": f"Decision recorded. Initiative is now at stage: {initiative.stage}",
        })


class InitiativeScoreView(generics.RetrieveAPIView):
    queryset = InitiativeScore.objects.select_related("initiative").all()
    serializer_class = InitiativeScoreSerializer

    def get_object(self):
        return InitiativeScore.objects.get(initiative_id=self.kwargs["pk"])


class DashboardStatsView(APIView):
    """Return funnel-level aggregates for the dashboard."""

    def get(self, request):
        qs = Initiative.objects.all()
        stage_counts = dict(
            qs.values_list("stage").annotate(count=Count("id")).values_list("stage", "count")
        )
        total = qs.count()
        awaiting = qs.filter(awaiting_decision=True).count()
        processing = qs.filter(ai_processing=True).count()
        approved = stage_counts.get("backlog", 0)
        rejected = stage_counts.get("rejected", 0)

        return Response({
            "total": total,
            "awaiting_decision": awaiting,
            "ai_processing": processing,
            "approved": approved,
            "rejected": rejected,
            "by_stage": stage_counts,
        })
