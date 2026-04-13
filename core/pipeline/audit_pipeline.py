"""
FNX Internal Audit Pipeline Node Definitions.

Defines the DAG structure for Bi-annual Internal Audits:

    ┌──────────────┐
    │ audit_assess │ (Evaluate Combat Answers + Historical Evidence)
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │   tld_map    │ (Calculate Technique, Language, Digital)
    └──────────────┘
           
"""

import os
from core.agents.audit_assessment_agent import AuditAssessmentAgent
from core.pipeline.dag_engine import DAGEngine
from core.store.base_store import StateStore
from core.taxonomy import get_taxonomy


def build_audit_pipeline(store: StateStore,
                        framework_path: str = None,
                        llm_provider: str = "gemini") -> DAGEngine:
    """
    Build and return a fully configured FNX Internal Audit pipeline DAG.
    Note: For Org Chart processing, the orchestrator should loop over employees
    and trigger this pipeline for each submission.
    """
    if framework_path is None:
        framework_path = os.path.join(
            os.path.dirname(__file__), "..", "..",
            "docs", "building-21", "framework_definition.md"
        )

    # Initialize agents
    audit_agent = AuditAssessmentAgent(framework_path, llm_provider)

    # Create DAG engine
    engine = DAGEngine(store)

    # ── Node: AUDIT ASSESS (LLM) ──
    def audit_assess_node(ctx):
        """Evaluate employee combat answers and historical evidence."""
        # ctx["submission"] should contain: employee_id, role, combat_context, combat_answers, historical_evidence
        result = audit_agent.assess(ctx.get("submission", {}))
        return result

    # ── Node: TLD MAP (Logic Layer) ──
    def tld_map_node(ctx):
        """
        Calculate TLD scores for the employee and format for heatmap.
        """
        audit_result = ctx["results"]["audit_assess"]
        comps = audit_result.get("competencies", [])
        
        tax = get_taxonomy()
        tld_data = getattr(tax, "tld_zones", {})
        if not tld_data and hasattr(tax, "data") and "tld_zones" in tax.data:
            tld_data = tax.data["tld_zones"]
            
        tld_scores = {}
        for zone_key, zone_info in tld_data.items():
            valid_codes = zone_info.get("competency_ids", [])
            levels = [c["level"] for c in comps if c.get("code") in valid_codes]
            avg_score = sum(levels) / len(levels) if levels else 0.0
            
            # Save using both UI Alias (Katz) and native TLD identifier
            ui_alias = zone_info.get("ui_alias", zone_key)
            tld_scores[ui_alias] = round(avg_score, 2)
            tld_scores[f"{zone_key}_native"] = round(avg_score, 2)
            
        audit_result["tld_scores"] = tld_scores
        
        return audit_result


    # Register nodes
    engine.add_node(
        name="audit_assess",
        handler=audit_assess_node,
        depends_on=[],
        max_retries=2,
    )

    engine.add_node(
        name="tld_map",
        handler=tld_map_node,
        depends_on=["audit_assess"], 
    )

    return engine
