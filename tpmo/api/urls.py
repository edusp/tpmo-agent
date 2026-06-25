from django.urls import path
from . import views

urlpatterns = [
    path("initiatives/", views.InitiativeListCreateView.as_view(), name="api-initiative-list"),
    path("initiatives/<uuid:pk>/", views.InitiativeDetailView.as_view(), name="api-initiative-detail"),
    path("initiatives/<uuid:pk>/trigger/", views.TriggerAgentView.as_view(), name="api-trigger-agent"),
    path("initiatives/<uuid:pk>/decide/", views.RecordDecisionView.as_view(), name="api-record-decision"),
    path("initiatives/<uuid:pk>/score/", views.InitiativeScoreView.as_view(), name="api-initiative-score"),
    path("dashboard/stats/", views.DashboardStatsView.as_view(), name="api-dashboard-stats"),
]
