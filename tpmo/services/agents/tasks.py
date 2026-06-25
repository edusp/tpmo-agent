"""
CrewAI task definitions for each PMO workflow stage.
Each builder returns a Task object with a detailed prompt and expected output spec.
"""

from crewai import Task


def build_intake_triage_task(agent, initiative_data: dict) -> Task:
    return Task(
        description=f"""
You are processing a new technology initiative submission for the Technology PMO.

## Initiative Details
- Title: {initiative_data.get('title')}
- Department: {initiative_data.get('department')}
- Submitter: {initiative_data.get('submitter_name')} ({initiative_data.get('submitter_email')})
- Description: {initiative_data.get('description')}
- Problem Statement: {initiative_data.get('problem_statement', 'Not provided')}
- Expected Benefits: {initiative_data.get('expected_benefits', 'Not provided')}
- Proposed Solution: {initiative_data.get('proposed_solution', 'Not provided')}
- Estimated Cost: {initiative_data.get('estimated_cost', 'Not provided')}
- Estimated Duration (months): {initiative_data.get('estimated_duration_months', 'Not provided')}
- Strategic Alignment: {initiative_data.get('strategic_alignment', 'Not provided')}

## Your Tasks
1. CLASSIFY the initiative: categorise it as Technology Enablement, Process Automation, Data & Analytics,
   Compliance & Risk, Customer Experience, or Infrastructure.
2. SIZE the initiative based on cost and complexity: Small (<$50K), Medium ($50K–$500K), or Large (>$500K).
3. VALIDATE completeness: score completeness 0–100 and list any critical missing fields.
4. DETECT duplicates: flag if this appears to overlap with other known initiatives (use your knowledge
   of common enterprise patterns; note you do not have access to the portfolio database in this task).
5. ROUTE the initiative: recommend Proceed, Hold for Information, or Reject with rationale.
6. LIST flags: any risks, dependencies, or governance concerns the reviewer should note.

## Output Format
Return a structured JSON object only. No prose outside the JSON.
""",
        expected_output="""
A valid JSON object with this structure:
{
  "classification": {
    "initiative_type": "string",
    "strategic_category": "string",
    "size": "small|medium|large",
    "completeness_score": 0-100,
    "missing_fields": ["field1", "field2"],
    "flags": ["flag1", "flag2"]
  },
  "duplicate_check": {
    "status": "No duplicates detected | Possible duplicate detected",
    "similar_initiatives": [],
    "notes": "string"
  },
  "triage_recommendation": {
    "action": "PROCEED | HOLD | REJECT",
    "priority_flag": "High | Medium | Low",
    "rationale": "string",
    "next_steps": ["step1", "step2"]
  }
}
""",
        agent=agent,
    )


def build_research_enrichment_task(agent, initiative_data: dict) -> Task:
    return Task(
        description=f"""
You are conducting research and enrichment for an initiative that has passed triage.

## Initiative
- Reference: {initiative_data.get('reference_code')}
- Title: {initiative_data.get('title')}
- Department: {initiative_data.get('department')}
- Problem Statement: {initiative_data.get('problem_statement')}
- Proposed Solution: {initiative_data.get('proposed_solution')}
- Size Classification: {initiative_data.get('size')}
- Estimated Cost: {initiative_data.get('estimated_cost', 'Not confirmed')}

## Triage Output
{initiative_data.get('triage_output', {})}

## Your Tasks
1. VALIDATE the problem statement — is it clearly articulated? What assumptions are embedded?
2. ASSESS technical feasibility (High / Medium / Low) with reasoning.
3. ANALYSE stakeholders — who are the likely key stakeholders, impacted groups, and decision-makers?
4. IDENTIFY risks — list the top 5 risks with likelihood and impact.
5. ENRICH cost estimate — provide a three-point estimate (Low / Most Likely / High) with basis.
6. SURFACE data gaps — clearly list what information is still needed before a brief can be authored.
7. SUMMARISE findings in a research brief suitable for handoff to the Documentation Author.

Do not fabricate specific vendor prices or regulatory requirements. State assumptions clearly.
""",
        expected_output="""
A valid JSON object with this structure:
{
  "problem_validation": {
    "is_valid": true,
    "clarity_score": 0-100,
    "embedded_assumptions": ["assumption1"],
    "recommended_clarifications": ["clarification1"]
  },
  "technical_feasibility": {
    "rating": "High|Medium|Low",
    "rationale": "string",
    "key_risks": ["risk1"],
    "dependencies": ["dep1"]
  },
  "stakeholder_analysis": {
    "executive_sponsor": "string",
    "primary_stakeholders": ["stakeholder1"],
    "impacted_groups": ["group1"],
    "sme_required": ["sme1"]
  },
  "risk_register": [
    {"risk": "string", "likelihood": "High|Medium|Low", "impact": "High|Medium|Low", "mitigation": "string"}
  ],
  "cost_estimate": {
    "low": 0,
    "most_likely": 0,
    "high": 0,
    "currency": "USD",
    "basis": "string",
    "confidence": "Low|Medium|High"
  },
  "data_gaps": ["gap1", "gap2"],
  "research_summary": "string"
}
""",
        agent=agent,
    )


def build_project_brief_task(agent, initiative_data: dict) -> Task:
    return Task(
        description=f"""
You are authoring a formal Project Brief for a technology initiative.

## Initiative
- Reference: {initiative_data.get('reference_code')}
- Title: {initiative_data.get('title')}
- Department: {initiative_data.get('department')}
- Size: {initiative_data.get('size')}
- Problem Statement: {initiative_data.get('problem_statement')}
- Expected Benefits: {initiative_data.get('expected_benefits')}
- Proposed Solution: {initiative_data.get('proposed_solution')}
- Strategic Alignment: {initiative_data.get('strategic_alignment')}

## Research Output Available
{initiative_data.get('research_output', {})}

## Your Tasks
Author a complete Project Brief following this structure. All sections must be populated.
Where information is unavailable, write "To Be Confirmed" and note what action is required.
The brief must be suitable for presentation to a Steering Committee.
Use plain, professional English. Avoid jargon.
""",
        expected_output="""
A valid JSON object with this structure:
{
  "executive_summary": "2-3 sentence summary for a busy executive",
  "problem_statement": "Clear articulation of the problem being solved",
  "proposed_solution": "What will be delivered and how",
  "scope": {
    "in_scope": ["item1", "item2"],
    "out_of_scope": ["item1"]
  },
  "benefits_realisation": {
    "financial_benefits": ["benefit1"],
    "non_financial_benefits": ["benefit2"],
    "kpis": [{"metric": "string", "target": "string", "timeline": "string"}]
  },
  "resource_requirements": {
    "estimated_budget": "string",
    "internal_effort_days": 0,
    "external_resources": "string",
    "technology_assets": ["asset1"]
  },
  "timeline": {
    "estimated_start": "string",
    "estimated_end": "string",
    "key_milestones": [{"milestone": "string", "target_date": "string"}]
  },
  "risks_and_assumptions": {
    "top_risks": [{"risk": "string", "mitigation": "string"}],
    "key_assumptions": ["assumption1"]
  },
  "governance": {
    "project_sponsor": "string",
    "steering_committee": "string",
    "reporting_cadence": "string"
  },
  "recommendation": "string — recommend Proceed to Business Case / Proceed to Scoring / Reject"
}
""",
        agent=agent,
    )


def build_business_case_task(agent, initiative_data: dict) -> Task:
    return Task(
        description=f"""
You are authoring a full Business Case for a Medium or Large technology initiative.

## Initiative
- Reference: {initiative_data.get('reference_code')}
- Title: {initiative_data.get('title')}
- Size: {initiative_data.get('size')}
- Brief Summary: {initiative_data.get('project_brief', {}).get('executive_summary', 'See full brief')}

## Project Brief & Research Available
Brief: {initiative_data.get('project_brief', {})}
Research: {initiative_data.get('research_output', {})}

## Your Tasks
Author a complete Business Case. It must cover:
1. Strategic alignment with corporate objectives
2. Options analysis (at minimum: do nothing, current proposal, alternative approach)
3. Detailed financial model (costs, benefits, NPV, IRR, payback period)
4. Risk assessment with mitigation strategies
5. Implementation approach and phasing
6. Governance and success measures
7. Executive recommendation

Be rigorous with financial calculations. State all assumptions clearly.
""",
        expected_output="""
A valid JSON object with this structure:
{
  "executive_summary": "string",
  "strategic_context": {
    "corporate_objectives_aligned": ["objective1"],
    "strategic_rationale": "string",
    "cost_of_inaction": "string"
  },
  "options_analysis": [
    {
      "option": "Do Nothing",
      "description": "string",
      "pros": ["pro1"],
      "cons": ["con1"],
      "estimated_cost": 0,
      "recommended": false
    }
  ],
  "financial_model": {
    "total_investment": 0,
    "annual_operating_cost": 0,
    "annual_savings": 0,
    "net_present_value": 0,
    "internal_rate_of_return": 0,
    "payback_period_months": 0,
    "roi_percentage": 0,
    "assumptions": ["assumption1"]
  },
  "risk_assessment": [
    {"risk": "string", "likelihood": "H|M|L", "impact": "H|M|L", "rating": "H|M|L", "mitigation": "string"}
  ],
  "implementation_approach": {
    "phases": [
      {"phase": "Phase 1", "description": "string", "duration_months": 0, "cost": 0}
    ],
    "dependencies": ["dep1"],
    "critical_success_factors": ["csf1"]
  },
  "governance_framework": {
    "sponsor": "string",
    "pmo_owner": "string",
    "reporting": "string",
    "post_implementation_review": "string"
  },
  "recommendation": {
    "decision": "APPROVE | REJECT | DEFER",
    "rationale": "string",
    "conditions": ["condition1"]
  }
}
""",
        agent=agent,
    )


def build_scoring_task(agent, initiative_data: dict) -> Task:
    return Task(
        description=f"""
You are scoring a technology initiative for portfolio prioritisation.

## Initiative
- Reference: {initiative_data.get('reference_code')}
- Title: {initiative_data.get('title')}
- Size: {initiative_data.get('size')}
- Department: {initiative_data.get('department')}

## Available Artefacts
Brief: {initiative_data.get('project_brief', {})}
Business Case: {initiative_data.get('business_case', {})}
Research: {initiative_data.get('research_output', {})}

## Scoring Framework

### Portfolio Strategy Score (PS) — each dimension scored 1–5
- Strategic Alignment (weight 30%): How well does this align to corporate strategy?
- Business Value (weight 30%): What is the magnitude of benefit delivered?
- Urgency (weight 20%): Is there a time-critical driver?
- Risk (weight 20%): Rate INVERSELY — 5 = very low risk, 1 = very high risk

### Solution Attractiveness Score (SAS) — each dimension scored 1–5
- Feasibility (weight 40%): How achievable is this with current capability?
- Complexity (weight 30%): Rate INVERSELY — 5 = low complexity, 1 = very complex
- Resource Availability (weight 30%): Are the required resources available?

### ROI Analysis
Calculate or estimate: ROI%, payback period, NPV if data is available.

### Composite Score
Composite = (PS_weighted * 50%) + (SAS_weighted * 30%) + (ROI_normalised * 20%)
Scale: 0–100

Provide full rationale for each score dimension. Do NOT make the funding decision.
""",
        expected_output="""
A valid JSON object with this structure:
{
  "portfolio_strategy_score": {
    "strategic_alignment": {"score": 1-5, "rationale": "string"},
    "business_value": {"score": 1-5, "rationale": "string"},
    "urgency": {"score": 1-5, "rationale": "string"},
    "risk_inverse": {"score": 1-5, "rationale": "string"},
    "weighted_total": 0.0
  },
  "solution_attractiveness_score": {
    "feasibility": {"score": 1-5, "rationale": "string"},
    "complexity_inverse": {"score": 1-5, "rationale": "string"},
    "resource_availability": {"score": 1-5, "rationale": "string"},
    "weighted_total": 0.0
  },
  "roi_analysis": {
    "roi_percentage": 0.0,
    "payback_months": 0,
    "npv": 0,
    "basis": "string"
  },
  "composite_score": 0.0,
  "priority_band": "High Priority | Medium Priority | Low Priority | Not Recommended",
  "recommendation": "string — what the analyst recommends for PRC consideration",
  "scoring_rationale": "string — overall narrative"
}
""",
        agent=agent,
    )


def build_prc_pack_task(agent, initiative_data: dict) -> Task:
    return Task(
        description=f"""
You are preparing a PRC (Project Review Committee) decision pack for an executive review.

## Initiative
- Reference: {initiative_data.get('reference_code')}
- Title: {initiative_data.get('title')}
- Size: {initiative_data.get('size')}
- Composite Score: {initiative_data.get('scoring_output', {}).get('composite_score', 'TBC')}

## Full Initiative Artefacts
Research: {initiative_data.get('research_output', {})}
Brief: {initiative_data.get('project_brief', {})}
Business Case: {initiative_data.get('business_case', {})}
Scoring: {initiative_data.get('scoring_output', {})}

## Your Tasks
Prepare a PRC decision pack. It must:
1. Be concise — executives read this in under 5 minutes
2. Lead with a one-paragraph executive summary
3. Present financial data clearly
4. Summarise the top 3 risks only
5. Show the scoring context (vs portfolio average if known)
6. Provide a governance recommendation WITH conditions
7. List required decisions and next steps
8. Include a compliance/governance checklist

You do NOT make the final decision. You prepare the pack for the PRC to decide.
Flag any governance concerns or missing approvals.
""",
        expected_output="""
A valid JSON object with this structure:
{
  "pack_metadata": {
    "reference": "string",
    "prepared_by": "AI Governance Officer",
    "review_date": "string",
    "classification": "CONFIDENTIAL"
  },
  "executive_summary": "string — 1 paragraph, max 150 words",
  "initiative_overview": {
    "title": "string",
    "department": "string",
    "sponsor": "string",
    "size": "string",
    "stage": "PRC Decision"
  },
  "financial_snapshot": {
    "total_investment": "string",
    "expected_roi": "string",
    "payback_period": "string",
    "npv": "string",
    "annual_run_cost": "string"
  },
  "top_risks": [
    {"risk": "string", "rating": "H|M|L", "mitigation": "string"}
  ],
  "scoring_context": {
    "composite_score": 0.0,
    "priority_band": "string",
    "portfolio_position": "string"
  },
  "compliance_checklist": [
    {"item": "string", "status": "PASS|FAIL|PENDING", "notes": "string"}
  ],
  "governance_recommendation": {
    "recommendation": "APPROVE | REJECT | DEFER",
    "rationale": "string",
    "conditions": ["condition1"],
    "approval_required_from": ["approver1"]
  },
  "required_decisions": ["decision1", "decision2"],
  "next_steps": ["step1", "step2"]
}
""",
        agent=agent,
    )
