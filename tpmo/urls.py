from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("intake/", views.intake, name="intake"),
    path("initiatives/<uuid:pk>/", views.initiative_detail, name="initiative-detail"),
    path("initiatives/<uuid:pk>/decide/", views.record_decision, name="record-decision"),
    path("initiatives/<uuid:pk>/prc/", views.prc_decision, name="prc-decision"),
]
