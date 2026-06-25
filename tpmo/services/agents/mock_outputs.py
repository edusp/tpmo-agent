"""
Realistic mock agent outputs for prototype demonstration.
Used when TPMO_MOCK_AGENTS=True or no LLM API key is configured.
Example initiative: Enterprise CRM Modernisation (TPMO-2026-0001)
"""


def get_mock_triage_output(initiative_data: dict) -> dict:
    title = initiative_data.get("title", "Unknown Initiative")
    dept = initiative_data.get("department", "Technology")
    cost = initiative_data.get("estimated_cost")

    if cost and float(cost) > 500_000:
        size = "large"
    elif cost and float(cost) > 50_000:
        size = "medium"
    else:
        size = "medium"  # default for prototype

    return {
        "classification": {
            "initiative_type": "Technology Enablement",
            "strategic_category": "Digital Transformation",
            "size": size,
            "completeness_score": 78,
            "missing_fields": [
                "Detailed ROI estimate with assumptions",
                "Technical architecture overview",
                "Vendor assessment / market comparison",
            ],
            "flags": [
                "Budget authority not formally confirmed",
                f"Dependency on {dept} capacity in Q3",
                "Regulatory impact assessment not included",
            ],
        },
        "duplicate_check": {
            "status": "No duplicates detected",
            "similar_initiatives": [],
            "notes": (
                f"No existing or recently rejected initiatives in the portfolio "
                f"match '{title}'. Deduplication check complete."
            ),
        },
        "triage_recommendation": {
            "action": "PROCEED",
            "priority_flag": "Medium",
            "rationale": (
                f"'{title}' aligns with the Digital Transformation strategic pillar "
                f"and addresses a documented operational gap in the {dept} division. "
                f"Submission completeness is 78% — the identified gaps are addressable "
                f"in the Research & Enrichment phase. No duplicates found."
            ),
            "next_steps": [
                "Assign Research Analyst from PMO team",
                "Request confirmed budget authority from Finance",
                "Schedule 45-minute stakeholder discovery session",
                "Obtain IT Architecture preliminary assessment",
            ],
        },
    }


def get_mock_research_output(initiative_data: dict) -> dict:
    cost = float(initiative_data.get("estimated_cost") or 250_000)
    return {
        "problem_validation": {
            "is_valid": True,
            "clarity_score": 82,
            "embedded_assumptions": [
                "Current system will not receive further vendor support",
                "User adoption rate will be >80% within 6 months",
                "Internal IT team can support implementation alongside BAU",
            ],
            "recommended_clarifications": [
                "Confirm end-of-support date from current vendor",
                "Validate the 80% adoption target against change management capacity",
            ],
        },
        "technical_feasibility": {
            "rating": "High",
            "rationale": (
                "The proposed technology stack is mature and widely adopted in the industry. "
                "The organisation has existing cloud infrastructure compatible with the solution. "
                "Integration with legacy ERP is achievable via standard API connectors."
            ),
            "key_risks": [
                "Data migration complexity from legacy system",
                "Integration with on-premise ERP v11 requires custom middleware",
                "SSO configuration requires Identity team involvement (6-week lead time)",
            ],
            "dependencies": [
                "Cloud Infrastructure team (network configuration)",
                "Identity & Access Management team (SSO)",
                "Finance ERP team (integration sign-off)",
            ],
        },
        "stakeholder_analysis": {
            "executive_sponsor": "Chief Operating Officer",
            "primary_stakeholders": [
                "Head of Operations",
                "IT Architecture Lead",
                "Finance Business Partner",
            ],
            "impacted_groups": [
                f"{initiative_data.get('department', 'Operations')} department (~150 users)",
                "IT Support (L1/L2 training required)",
                "Vendor Management team",
            ],
            "sme_required": [
                "Data Migration Specialist",
                "Change Management Lead",
                "Procurement (vendor contracts)",
            ],
        },
        "risk_register": [
            {
                "risk": "Data migration errors causing business disruption",
                "likelihood": "Medium",
                "impact": "High",
                "mitigation": "Parallel run period of 4 weeks; data reconciliation UAT gate",
            },
            {
                "risk": "Low user adoption due to change fatigue",
                "likelihood": "Medium",
                "impact": "Medium",
                "mitigation": "Dedicated change management programme; super-user network",
            },
            {
                "risk": "Integration with ERP delayed beyond schedule",
                "likelihood": "Low",
                "impact": "High",
                "mitigation": "Integration work begins in Phase 1; fallback manual process defined",
            },
            {
                "risk": "Budget overrun due to scope creep",
                "likelihood": "Medium",
                "impact": "Medium",
                "mitigation": "Fixed-scope Phase 1; change control process enforced from Day 1",
            },
            {
                "risk": "Vendor delivery capability risk",
                "likelihood": "Low",
                "impact": "High",
                "mitigation": "Proof of concept required before contract signature; penalty clauses",
            },
        ],
        "cost_estimate": {
            "low": round(cost * 0.8),
            "most_likely": round(cost),
            "high": round(cost * 1.3),
            "currency": "USD",
            "basis": "Analogous estimation from 3 similar implementations; vendor indicative quote received",
            "confidence": "Medium",
        },
        "data_gaps": [
            "Final vendor pricing not confirmed (indicative only)",
            "IT capacity impact on BAU not yet assessed",
            "Legal review of vendor contract not initiated",
            "Training cost estimate not included in current figures",
        ],
        "research_summary": (
            f"The initiative '{initiative_data.get('title')}' addresses a clearly validated "
            f"operational problem. Technical feasibility is rated HIGH. The primary risks relate "
            f"to data migration and change management, both of which are manageable with standard "
            f"PMO controls. The cost estimate (most likely: ${cost:,.0f}) is based on analogous "
            f"projects and carries medium confidence pending vendor confirmation. "
            f"The initiative is ready for Project Brief authoring subject to closing 4 identified data gaps."
        ),
    }


def get_mock_project_brief(initiative_data: dict) -> dict:
    cost = float(initiative_data.get("estimated_cost") or 250_000)
    title = initiative_data.get("title", "Technology Initiative")
    dept = initiative_data.get("department", "Operations").title()
    size = initiative_data.get("size", "medium")
    months = initiative_data.get("estimated_duration_months") or 9

    return {
        "executive_summary": (
            f"'{title}' is a {size}-scale technology initiative proposed by {dept} to address "
            f"a critical operational gap. The initiative will deliver measurable efficiency gains "
            f"and is aligned to the Digital Transformation strategic objective. Total investment "
            f"is estimated at ${cost:,.0f} over {months} months with a projected ROI of 35%."
        ),
        "problem_statement": (
            initiative_data.get("problem_statement")
            or f"The {dept} division currently operates on legacy technology that limits "
            f"scalability, introduces manual processing risk, and creates a dependency on "
            f"vendor support that is approaching end-of-life. This results in operational "
            f"inefficiency, increasing error rates, and an inability to meet growing demand."
        ),
        "proposed_solution": (
            initiative_data.get("proposed_solution")
            or f"Implementation of a cloud-native platform to replace the current system, "
            f"delivered in two phases: Phase 1 (core migration) and Phase 2 (advanced features). "
            f"The solution will integrate with existing ERP and HR systems via standard APIs."
        ),
        "scope": {
            "in_scope": [
                "Core platform implementation and configuration",
                "Data migration from legacy system",
                "Integration with Finance ERP (read-only)",
                "User training and change management",
                "Hypercare support for 90 days post go-live",
            ],
            "out_of_scope": [
                "ERP system upgrades",
                "Mobile application development",
                "Third-party reporting tool integration (Phase 2)",
            ],
        },
        "benefits_realisation": {
            "financial_benefits": [
                f"Reduction in manual processing cost: ~$45,000/year",
                "Elimination of legacy maintenance fees: ~$30,000/year",
                "Error reduction estimated at 60%, saving ~$20,000/year in rework",
            ],
            "non_financial_benefits": [
                "Improved user experience and staff satisfaction",
                "Real-time data visibility for management reporting",
                "Reduced vendor dependency and improved business continuity",
                "Scalable platform to support 3-year growth plan",
            ],
            "kpis": [
                {"metric": "Process automation rate", "target": ">70%", "timeline": "Month 6"},
                {"metric": "User adoption rate", "target": ">80%", "timeline": "Month 3"},
                {"metric": "Error/rework rate", "target": "<5%", "timeline": "Month 9"},
                {"metric": "System uptime", "target": "99.9%", "timeline": "Ongoing"},
            ],
        },
        "resource_requirements": {
            "estimated_budget": f"${cost:,.0f} (most likely); range ${cost*0.8:,.0f}–${cost*1.3:,.0f}",
            "internal_effort_days": 120,
            "external_resources": "Implementation partner (vendor-certified); Change Management consultant",
            "technology_assets": ["Cloud hosting (existing contract)", "API gateway licences", "Training environment"],
        },
        "timeline": {
            "estimated_start": "Month 1 post-approval",
            "estimated_end": f"Month {months} post-approval",
            "key_milestones": [
                {"milestone": "Vendor selection and contract", "target_date": "Month 2"},
                {"milestone": "Data migration complete (UAT)", "target_date": f"Month {months - 3}"},
                {"milestone": "Go-live (Phase 1)", "target_date": f"Month {months - 1}"},
                {"milestone": "Hypercare complete / BAU handover", "target_date": f"Month {months + 2}"},
            ],
        },
        "risks_and_assumptions": {
            "top_risks": [
                {
                    "risk": "Data migration complexity exceeds estimate",
                    "mitigation": "Early data audit; dedicated migration specialist",
                },
                {
                    "risk": "Low user adoption",
                    "mitigation": "Change management programme and super-user network",
                },
                {
                    "risk": "Integration delays with ERP",
                    "mitigation": "Integration workstream begins Week 1; fallback manual process defined",
                },
            ],
            "key_assumptions": [
                "Board approval received by end of current quarter",
                "Internal IT team available for 2 days/week throughout project",
                "No major organisational restructure during project period",
            ],
        },
        "governance": {
            "project_sponsor": "COO / Divisional GM",
            "steering_committee": "Monthly — Sponsor, CIO, Finance Director, PMO Lead",
            "reporting_cadence": "Fortnightly status report; monthly steering committee",
        },
        "recommendation": (
            f"PROCEED TO {'BUSINESS CASE' if size in ('medium', 'large') else 'SCORING'}. "
            f"The initiative has a valid business case, is technically feasible, and aligns "
            f"to strategic priorities. {'A full Business Case is required given the investment level.' if size in ('medium','large') else ''}"
        ),
    }


def get_mock_business_case(initiative_data: dict) -> dict:
    cost = float(initiative_data.get("estimated_cost") or 250_000)
    title = initiative_data.get("title", "Technology Initiative")
    annual_savings = cost * 0.35
    npv = annual_savings * 3 - cost

    return {
        "executive_summary": (
            f"This Business Case recommends approval of '{title}' at an investment of "
            f"${cost:,.0f}. The initiative delivers a projected ROI of 35%, NPV of "
            f"${npv:,.0f} over 3 years, and a payback period of 18 months. "
            f"The preferred option (Option B: cloud-native platform) outperforms alternatives "
            f"on cost, risk, and strategic alignment."
        ),
        "strategic_context": {
            "corporate_objectives_aligned": [
                "Digital Transformation 2025–2027",
                "Operational Excellence Programme",
                "Cost Efficiency Initiative",
            ],
            "strategic_rationale": (
                "The initiative directly supports the Digital Transformation roadmap by replacing "
                "legacy infrastructure and enabling data-driven decision-making. It is a dependency "
                "for two other strategic programmes scheduled for 2027."
            ),
            "cost_of_inaction": (
                f"Without investment, legacy maintenance costs will increase by 15% annually "
                f"(est. $30K/year). Operational errors will continue at current rate, costing "
                f"~$20K/year in rework. Vendor end-of-support expiry in 18 months introduces "
                f"a critical business continuity risk."
            ),
        },
        "options_analysis": [
            {
                "option": "Option A — Do Nothing",
                "description": "Continue operating on current legacy system with no changes.",
                "pros": ["No upfront investment", "No change management required"],
                "cons": [
                    "Vendor support expires in 18 months (critical risk)",
                    "Ongoing costs increase 15%/year",
                    "Cannot support growth targets",
                ],
                "estimated_cost": 90_000,
                "recommended": False,
            },
            {
                "option": "Option B — Cloud-Native Platform (Recommended)",
                "description": "Full implementation of a cloud-native replacement platform.",
                "pros": [
                    "Full strategic alignment",
                    "Scalable for 5-year growth",
                    "35% ROI over 3 years",
                    "Eliminates vendor dependency risk",
                ],
                "cons": ["Higher upfront investment", "Change management required"],
                "estimated_cost": round(cost),
                "recommended": True,
            },
            {
                "option": "Option C — Hybrid / Lift-and-Shift",
                "description": "Migrate existing system to cloud without re-engineering.",
                "pros": ["Lower upfront cost", "Faster delivery"],
                "cons": [
                    "Does not resolve underlying technical debt",
                    "Limited scalability",
                    "12% ROI only",
                ],
                "estimated_cost": round(cost * 0.55),
                "recommended": False,
            },
        ],
        "financial_model": {
            "total_investment": round(cost),
            "annual_operating_cost": round(cost * 0.08),
            "annual_savings": round(annual_savings),
            "net_present_value": round(npv),
            "internal_rate_of_return": 28.5,
            "payback_period_months": 18,
            "roi_percentage": 35.0,
            "assumptions": [
                "Discount rate 8% (WACC)",
                "3-year evaluation horizon",
                "Annual savings materialise from Month 9",
                "No inflation adjustment applied",
                "Training costs included in total investment",
            ],
        },
        "risk_assessment": [
            {
                "risk": "Data migration errors",
                "likelihood": "M",
                "impact": "H",
                "rating": "H",
                "mitigation": "Parallel run; reconciliation gate; rollback plan",
            },
            {
                "risk": "Budget overrun (scope creep)",
                "likelihood": "M",
                "impact": "M",
                "rating": "M",
                "mitigation": "Fixed-scope Phase 1; formal change control from Day 1; 15% contingency included",
            },
            {
                "risk": "User adoption failure",
                "likelihood": "L",
                "impact": "H",
                "rating": "M",
                "mitigation": "Dedicated OCM lead; super-user network; 90-day hypercare",
            },
        ],
        "implementation_approach": {
            "phases": [
                {
                    "phase": "Phase 1 — Foundation",
                    "description": "Core platform setup, data migration, integration, UAT",
                    "duration_months": 6,
                    "cost": round(cost * 0.75),
                },
                {
                    "phase": "Phase 2 — Optimisation",
                    "description": "Advanced features, reporting, automation workflows",
                    "duration_months": 3,
                    "cost": round(cost * 0.25),
                },
            ],
            "dependencies": [
                "ERP team capacity confirmed",
                "Cloud infrastructure provisioned",
                "Procurement contract signed",
            ],
            "critical_success_factors": [
                "Executive sponsor active and visible",
                "Dedicated internal project manager (not split role)",
                "Data quality audit completed before migration",
            ],
        },
        "governance_framework": {
            "sponsor": "COO",
            "pmo_owner": "Technology PMO",
            "reporting": "Fortnightly status to Steering Committee; Monthly to PRC",
            "post_implementation_review": "90 days post go-live; 12-month benefits realisation review",
        },
        "recommendation": {
            "decision": "APPROVE",
            "rationale": (
                "Option B delivers the strongest strategic, financial, and risk outcome. "
                "The investment is justified by a 35% ROI, NPV positive outcome, and "
                "elimination of a critical business continuity risk. All feasibility gates have been passed."
            ),
            "conditions": [
                "Project Manager appointed before contract signature",
                "Data quality audit completed in Month 1",
                "Monthly benefits realisation reporting from Month 9",
                "PRC retains right to review at Phase 2 gate",
            ],
        },
    }


def get_mock_scoring_output(initiative_data: dict) -> dict:
    return {
        "portfolio_strategy_score": {
            "strategic_alignment": {
                "score": 4,
                "rationale": "Directly supports Digital Transformation and Operational Excellence pillars.",
            },
            "business_value": {
                "score": 4,
                "rationale": "35% ROI, NPV positive, and resolves a critical operational risk.",
            },
            "urgency": {
                "score": 4,
                "rationale": "Vendor end-of-support in 18 months creates a hard deadline.",
            },
            "risk_inverse": {
                "score": 3,
                "rationale": "Medium residual risk profile; data migration and change management are manageable.",
            },
            "weighted_total": 3.75,
        },
        "solution_attractiveness_score": {
            "feasibility": {
                "score": 4,
                "rationale": "Cloud-native approach is well-understood; vendor certified resources available.",
            },
            "complexity_inverse": {
                "score": 3,
                "rationale": "Integration with legacy ERP introduces moderate complexity; manageable with experienced team.",
            },
            "resource_availability": {
                "score": 3,
                "rationale": "IT capacity partially constrained; 2 days/week available internally; vendor resource required.",
            },
            "weighted_total": 3.3,
        },
        "roi_analysis": {
            "roi_percentage": 35.0,
            "payback_months": 18,
            "npv": 87_500,
            "basis": "3-year horizon, 8% discount rate, savings materialise Month 9",
        },
        "composite_score": 78.5,
        "priority_band": "High Priority",
        "recommendation": (
            "This initiative scores in the HIGH PRIORITY band (78.5/100). "
            "Strong strategic alignment, confirmed business value, and a time-critical driver "
            "support a recommendation for PRC approval. The PMO recommends this initiative "
            "be included in the next PRC agenda for funding decision."
        ),
        "scoring_rationale": (
            "PS Score (3.75/5.0) reflects strong strategic and value dimensions, with urgency "
            "driven by the vendor end-of-support deadline. SAS Score (3.3/5.0) reflects a "
            "feasible but moderately complex delivery. ROI of 35% is above the 25% organisational "
            "hurdle rate. Composite score of 78.5 places this initiative in the top quartile "
            "of the current portfolio."
        ),
    }


def get_mock_prc_pack(initiative_data: dict) -> dict:
    from django.utils import timezone
    cost = float(initiative_data.get("estimated_cost") or 250_000)
    title = initiative_data.get("title", "Technology Initiative")
    ref = initiative_data.get("reference_code", "TPMO-2026-XXXX")

    return {
        "pack_metadata": {
            "reference": ref,
            "prepared_by": "AI Governance Officer (tPMO System)",
            "review_date": timezone.now().strftime("%d %B %Y"),
            "classification": "CONFIDENTIAL — PRC ONLY",
        },
        "executive_summary": (
            f"'{title}' ({ref}) is a {initiative_data.get('size', 'medium').upper()}-scale "
            f"technology initiative requesting ${cost:,.0f} in capital investment. "
            f"The initiative scores 78.5/100 on the PMO composite scoring model (HIGH PRIORITY). "
            f"A full Business Case has been completed, showing a 35% ROI over 3 years and "
            f"18-month payback. The PMO recommends APPROVAL subject to three conditions outlined below."
        ),
        "initiative_overview": {
            "title": title,
            "department": initiative_data.get("department", "Operations").title(),
            "sponsor": "COO",
            "size": initiative_data.get("size", "medium").title(),
            "stage": "PRC Decision",
        },
        "financial_snapshot": {
            "total_investment": f"${cost:,.0f}",
            "expected_roi": "35%",
            "payback_period": "18 months",
            "npv": f"${cost * 0.35:,.0f}",
            "annual_run_cost": f"${cost * 0.08:,.0f}/year",
        },
        "top_risks": [
            {
                "risk": "Data migration errors causing business disruption",
                "rating": "H",
                "mitigation": "Parallel run period; formal reconciliation gate before cutover",
            },
            {
                "risk": "IT resource availability constraint",
                "rating": "M",
                "mitigation": "Internal capacity confirmed at 2 days/week; vendor resources supplement",
            },
            {
                "risk": "Scope creep leading to budget overrun",
                "rating": "M",
                "mitigation": "Fixed-scope Phase 1; formal change control; 15% contingency held in reserve",
            },
        ],
        "scoring_context": {
            "composite_score": 78.5,
            "priority_band": "High Priority",
            "portfolio_position": "Top quartile — ranked above portfolio average of 62.0",
        },
        "compliance_checklist": [
            {"item": "Business Case completed and reviewed", "status": "PASS", "notes": ""},
            {"item": "Budget authority confirmed", "status": "PENDING", "notes": "Awaiting Finance sign-off"},
            {"item": "Legal/Procurement review", "status": "PENDING", "notes": "Contract review in progress"},
            {"item": "IT Architecture review", "status": "PASS", "notes": "Approved by Architecture Board"},
            {"item": "Security & Privacy impact assessment", "status": "PASS", "notes": "No PII in scope; low risk"},
            {"item": "Vendor due diligence", "status": "PASS", "notes": "Preferred vendor shortlisted"},
        ],
        "governance_recommendation": {
            "recommendation": "APPROVE",
            "rationale": (
                "The initiative meets all financial and strategic approval criteria. "
                "Business Case demonstrates a positive NPV and above-hurdle ROI. "
                "Two compliance items remain PENDING but are in-flight and do not constitute "
                "a blocker to approval in principle."
            ),
            "conditions": [
                "Finance budget authority confirmed before contract signature",
                "Legal/Procurement contract review completed before vendor engagement",
                "Project Manager appointed within 10 business days of approval",
            ],
            "approval_required_from": ["CIO", "CFO", "COO (Sponsor)"],
        },
        "required_decisions": [
            "1. APPROVE / REJECT / DEFER the initiative for funding",
            "2. Confirm budget allocation (CAPEX vs OPEX split)",
            "3. Confirm PRC conditions and monitoring requirements",
        ],
        "next_steps": [
            "PMO to issue approval letter within 2 business days",
            "Sponsor to appoint Project Manager",
            "Finance to confirm budget codes",
            "PMO to schedule project kick-off within 3 weeks of approval",
        ],
    }
