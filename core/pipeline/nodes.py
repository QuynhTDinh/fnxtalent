"""
FNX Pipeline Node Definitions.

Defines the actual DAG structure:

    ┌──────────┐       ┌──────────┐
    │ assess   │       │ decode   │     ← Run in PARALLEL
    └────┬─────┘       └────┬─────┘
         │                  │
         ▼                  ▼
    ┌────────────────────────────┐
    │    cross_validate          │     ← Validates both results
    └────────────┬───────────────┘
                 │
                 ▼
    ┌──────────────────┐
    │     match         │             ← Only runs if validation passes
    └──────────────────┘
"""

import os
from core.agents.assessment_agent import AssessmentAgent
from core.agents.jd_decoder_agent import JDDecoderAgent
from core.agents.matching_agent import MatchingAgent
from core.pipeline.dag_engine import DAGEngine
from core.store.base_store import StateStore


def build_fnx_pipeline(store: StateStore,
                        framework_path: str = None,
                        llm_provider: str = "gemini") -> DAGEngine:
    """
    Build and return a fully configured FNX pipeline DAG.
    """
    # Resolve framework path
    if framework_path is None:
        framework_path = os.path.join(
            os.path.dirname(__file__), "..", "..",
            "docs", "building-21", "framework_definition.md"
        )

    # Initialize agents
    assessment_agent = AssessmentAgent(framework_path, llm_provider)
    jd_decoder_agent = JDDecoderAgent(framework_path, llm_provider)
    matching_agent = MatchingAgent(framework_path)

    # Create DAG engine
    engine = DAGEngine(store)

    # ── Node: ASSESS (LLM) ──
    def assess_node(ctx):
        """Evaluate candidate competencies against Building 21."""
        result = assessment_agent.assess(ctx["candidate"])
        return result

    # ── Node: DECODE (LLM) ──
    def decode_node(ctx):
        """Decode JD into requirement matrix."""
        result = jd_decoder_agent.decode(ctx["job"])
        return result

    # ── Node: CROSS-VALIDATE (Logic) ──
    def cross_validate_node(ctx):
        """
        Cross-check assessment and JD results for consistency.

        Checks:
        1. Assessment returned at least 1 competency
        2. JD returned at least 1 requirement
        3. All competency levels are within 1-5
        4. At least 1 overlapping competency code exists
        """
        assess_result = ctx["results"].get("assess", {})
        decode_result = ctx["results"].get("decode", {})

        issues = []

        # Check 1: Non-empty results
        comps = assess_result.get("competencies", [])
        reqs = decode_result.get("required_competencies", [])

        if len(comps) == 0:
            issues.append("Assessment returned 0 competencies")
        if len(reqs) == 0:
            issues.append("JD decode returned 0 requirements")

        # Check 2: Valid levels (1-5)
        for c in comps:
            if not (1 <= c.get("level", 0) <= 5):
                issues.append(f"Invalid level {c.get('level')} for {c.get('code')}")
        for r in reqs:
            if not (1 <= r.get("target_level", 0) <= 5):
                issues.append(f"Invalid target_level {r.get('target_level')} for {r.get('code')}")

        # Check 3: At least some overlap
        assess_codes = {c.get("code") for c in comps}
        jd_codes = {r.get("code") for r in reqs}
        overlap = assess_codes & jd_codes

        if len(comps) > 0 and len(reqs) > 0 and len(overlap) == 0:
            # Warning but not a hard failure — different competency codes are possible
            issues.append(
                f"WARNING: No overlapping codes between assessment ({assess_codes}) "
                f"and JD ({jd_codes}). Match score may be low."
            )

        # Verdict
        is_valid = not any(
            issue for issue in issues
            if not issue.startswith("WARNING")
        )

        result = {
            "valid": is_valid,
            "checks_passed": len(comps) > 0 and len(reqs) > 0,
            "overlap_codes": list(overlap),
            "overlap_count": len(overlap),
            "issues": issues,
        }

        if issues:
            print(f"[CrossValidator] Issues: {issues}")
        else:
            print(f"[CrossValidator] All checks passed. Overlap: {overlap}")

        return result

    # ── Node: MATCH (Computation) ──
    def match_node(ctx):
        """Calculate fit score from validated results."""
        assess_result = ctx["results"]["assess"]
        decode_result = ctx["results"]["decode"]
        result = matching_agent.match(assess_result, decode_result)
        return result

    # ── Register nodes in DAG ──

    engine.add_node(
        name="assess",
        handler=assess_node,
        depends_on=[],          # No dependencies → can run immediately
        max_retries=2,
    )

    engine.add_node(
        name="decode",
        handler=decode_node,
        depends_on=[],          # No dependencies → runs PARALLEL with assess
        max_retries=2,
    )

    engine.add_node(
        name="cross_validate",
        handler=cross_validate_node,
        depends_on=["assess", "decode"],  # Waits for BOTH to complete
        is_validator=True,
        max_retries=0,          # Validators don't retry themselves
        on_fail="stop",         # Stop pipeline if validation fails
    )

    engine.add_node(
        name="match",
        handler=match_node,
        depends_on=["cross_validate"],  # Only runs after validation passes
        max_retries=1,
    )

    return engine
