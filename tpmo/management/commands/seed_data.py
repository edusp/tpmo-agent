"""
Management command: python manage.py seed_data

Creates realistic demo initiatives at various lifecycle stages so the
prototype dashboard is populated from the start.
"""

from django.core.management.base import BaseCommand
from tpmo.models import Initiative, AuditLog, Decision
from tpmo.services import workflow


SAMPLE_INITIATIVES = [
    {
        "title": "Enterprise CRM Modernisation",
        "description": "Replace the end-of-life Salesforce Classic instance with HubSpot Enterprise to support 500+ sales users and modern workflow automation.",
        "submitter_name": "Sarah Chen",
        "submitter_email": "s.chen@company.com",
        "department": "sales",
        "business_sponsor": "VP Sales",
        "problem_statement": "Salesforce Classic reaches end-of-support in Q2 2027. Current platform cannot support pipeline automation, AI scoring, or mobile field use. Manual workarounds cost the team 8 hours/week each.",
        "expected_benefits": "60% reduction in manual data entry, real-time pipeline visibility, 15% improvement in conversion tracking accuracy, elimination of $45K/year maintenance costs.",
        "proposed_solution": "HubSpot Enterprise CRM with phased migration: Phase 1 core migration (6 months), Phase 2 automation & reporting (3 months).",
        "strategic_alignment": "Digital Transformation 2025–2027, Sales Excellence Programme",
        "estimated_cost": 380000,
        "estimated_duration_months": 9,
        "dependencies": "Identity Management (SSO), Finance ERP integration",
        "constraints": "Must not disrupt Q4 sales cycle; go-live latest April 2027",
        "run_through": "full",  # run all stages
    },
    {
        "title": "Automated AP Invoice Processing",
        "description": "Implement AI-powered invoice OCR and automated 3-way matching to eliminate manual AP processing in the Finance team.",
        "submitter_name": "Mark Johnson",
        "submitter_email": "m.johnson@company.com",
        "department": "finance",
        "business_sponsor": "CFO",
        "problem_statement": "Finance team processes 4,500 invoices per month manually. Error rate is 3.2%, late payment penalties cost $28K/year, and two FTEs spend 70% of time on data entry.",
        "expected_benefits": "85% reduction in manual processing time, <0.5% error rate, $28K/year penalty elimination, 1.5 FTE capacity freed for higher-value work.",
        "proposed_solution": "ABBYY FlexiCapture with ERP integration. AI OCR extracts invoice data; automated matching; exception queue for manual review.",
        "strategic_alignment": "Cost Efficiency Initiative, Operational Excellence Programme",
        "estimated_cost": 125000,
        "estimated_duration_months": 5,
        "dependencies": "ERP team (integration), Procurement (vendor contract)",
        "constraints": "Must be compliant with audit requirements; GDPR-compliant data handling",
        "run_through": "scoring",  # run up to scoring
    },
    {
        "title": "Data Analytics Platform Upgrade",
        "description": "Upgrade from legacy BI tool (Crystal Reports) to a modern self-service analytics platform (Tableau Cloud) to enable data-driven decision making.",
        "submitter_name": "Alex Torres",
        "submitter_email": "a.torres@company.com",
        "department": "technology",
        "business_sponsor": "CTO",
        "problem_statement": "Current Crystal Reports environment requires IT involvement for every report change. Business users cannot self-serve. Report refresh takes 4–6 hours. Platform is 12 years old with no API support.",
        "expected_benefits": "Self-service analytics for 200+ business users, real-time data access, IT dependency eliminated for standard reporting, 70% faster decision cycle.",
        "proposed_solution": "Tableau Cloud with Snowflake data warehouse layer. Phased rollout by department.",
        "strategic_alignment": "Data & Analytics Strategy 2025, Digital Transformation",
        "estimated_cost": 210000,
        "estimated_duration_months": 7,
        "dependencies": "Cloud infrastructure (Azure), Data Governance team",
        "constraints": "Data sovereignty — all data must remain in Australian region",
        "run_through": "brief",
    },
    {
        "title": "Employee Onboarding Portal",
        "description": "Build a self-service onboarding portal for new employees to complete compliance training, submit documentation, and receive equipment requests without HR manual coordination.",
        "submitter_name": "Priya Patel",
        "submitter_email": "p.patel@company.com",
        "department": "hr",
        "business_sponsor": "CHRO",
        "problem_statement": "New employee onboarding takes 3–5 days of HR coordinator time per hire. 40% of new joiners report a poor first-week experience. Compliance training completion tracking is manual.",
        "expected_benefits": "Reduce onboarding admin to <4 hours/hire, improve new joiner NPS by 30 points, 100% automated compliance completion tracking.",
        "proposed_solution": "Low-code portal (ServiceNow or Microsoft Power Apps) integrated with HR system (Workday) and IT asset management.",
        "strategic_alignment": "People & Culture Strategy, Digital Workplace Programme",
        "estimated_cost": 85000,
        "estimated_duration_months": 4,
        "dependencies": "Workday integration, IT Asset Management system",
        "constraints": "Privacy Act compliance required; accessibility (WCAG 2.1 AA)",
        "run_through": "triage",
    },
    {
        "title": "Network Infrastructure Refresh",
        "description": "Replace aging core network switches (end-of-life Cisco Catalyst 2960 series) across 3 office locations to restore performance and eliminate security vulnerabilities.",
        "submitter_name": "James Wilson",
        "submitter_email": "j.wilson@company.com",
        "department": "technology",
        "business_sponsor": "CIO",
        "problem_statement": "Core switches are 8+ years old, past end-of-support. Two unplanned outages in Q1 2026 caused $45K in lost productivity. Security patches no longer available.",
        "expected_benefits": "Eliminate outage risk, meet security compliance requirements, 10Gb backbone enabling future cloud connectivity.",
        "proposed_solution": "Cisco Catalyst 9300 series refresh across Sydney HQ, Melbourne, Brisbane. 18-month hardware warranty + SmartNet.",
        "strategic_alignment": "IT Security & Risk Programme, Infrastructure Modernisation",
        "estimated_cost": 320000,
        "estimated_duration_months": 6,
        "dependencies": "Facilities (rack space), Procurement (Cisco partner contract)",
        "constraints": "Implementation must avoid business hours; max 4-hour maintenance windows",
        "run_through": "intake",
    },
]


def run_to_stage(initiative, target):
    """Run AI agents and apply stub decisions to progress initiative to target stage."""
    stage_order = ["intake", "triage", "research", "brief", "business_case", "scoring", "prc", "full"]

    if target == "intake":
        # Just run intake agent, leave at triage awaiting decision
        workflow.trigger_agents(initiative)
        return

    # intake → triage (run agents, then approve triage)
    workflow.trigger_agents(initiative)
    if target == "triage":
        return

    # Approve triage → research
    workflow.record_decision(initiative, "triage", "approve", "Approved by PMO — valid initiative, proceeding to research.", "PMO Lead")
    if initiative.stage != "research" or target == "triage":
        return

    # research → brief
    workflow.trigger_agents(initiative)
    workflow.record_decision(initiative, "brief_review", "approve", "Research complete. Proceeding to brief.", "PMO Lead")
    if target == "brief":
        return

    # brief → (business_case or scoring based on size)
    workflow.trigger_agents(initiative)
    if target == "brief":
        return

    if initiative.stage == "business_case":
        workflow.trigger_agents(initiative)
        workflow.record_decision(initiative, "bc_review", "approve", "Business case reviewed and approved. Proceeding to scoring.", "Finance Director")
        if target == "scoring" or initiative.stage == "scoring":
            workflow.trigger_agents(initiative)
        if target == "scoring":
            return
    elif initiative.stage == "scoring":
        workflow.trigger_agents(initiative)
        if target == "scoring":
            return

    # scoring → prc
    workflow.record_decision(initiative, "scoring_review", "approve", "Scoring reviewed. Proceeding to PRC.", "Portfolio Manager")
    if initiative.stage == "prc":
        workflow.trigger_agents(initiative)

    if target == "prc" or target == "full":
        return


class Command(BaseCommand):
    help = "Seed demo initiatives at various lifecycle stages"

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true", help="Clear existing data before seeding")

    def handle(self, *args, **options):
        if options["clear"]:
            Initiative.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared all existing initiatives."))

        created_count = 0
        for data in SAMPLE_INITIATIVES:
            run_through = data.pop("run_through")

            if Initiative.objects.filter(title=data["title"]).exists():
                self.stdout.write(f"  Skipping '{data['title']}' — already exists.")
                continue

            initiative = Initiative.objects.create(**data, stage="intake", ai_processing=False, awaiting_decision=False)
            AuditLog.objects.create(
                initiative=initiative,
                action="submitted",
                actor=data["submitter_name"],
                details={"source": "seed_data"},
            )

            self.stdout.write(f"  Created {initiative.reference_code}: {initiative.title}")
            try:
                run_to_stage(initiative, run_through)
                initiative.refresh_from_db()
                self.stdout.write(self.style.SUCCESS(f"    → Stage: {initiative.stage} | Awaiting: {initiative.awaiting_decision}"))
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f"    ✗ Error progressing to {run_through}: {exc}"))

            created_count += 1

        self.stdout.write(self.style.SUCCESS(f"\nSeeding complete. {created_count} initiative(s) created."))
        self.stdout.write("Visit http://127.0.0.1:8000/ to see the dashboard.")
