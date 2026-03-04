"""
MatchingAgent — Calculates fit score between candidate competencies and JD requirements.
Pure computation, no LLM needed.
"""

from .base_agent import BaseAgent


class MatchingAgent(BaseAgent):
    def __init__(self, framework_path=None):
        super().__init__("MatchingAgent", framework_path)

    def handle_event(self, event_name, data):
        pass  # Not used in DAG mode — DAG calls match() directly

    def match(self, assessment_result, jd_result):
        """Calculate fit score from assessment + JD results."""
        candidate_id = assessment_result.get("candidateId",
                       assessment_result.get("candidate_id", "unknown"))
        job_id = jd_result.get("job_id", "unknown")

        self.log(f"Matching Candidate {candidate_id} ↔ Job {job_id}")

        cand_comps = {c['code']: c for c in assessment_result.get('competencies', [])}
        required_comps = jd_result.get('required_competencies', [])

        priority_weights = {"High": 1.0, "Medium": 0.6, "Low": 0.3}
        gaps = []
        strengths = []
        total_fit = 0
        weights_sum = 0

        for req in required_comps:
            code = req['code']
            target = req['target_level']
            priority = req.get('priority', 'Medium')
            weight = priority_weights.get(priority, 0.6)

            cand = cand_comps.get(code, {})
            cand_lvl = cand.get('level', 0)

            fit = min(1.0, cand_lvl / target) if target > 0 else 1.0
            total_fit += fit * weight
            weights_sum += weight

            if cand_lvl < target:
                gaps.append({
                    "code": code,
                    "name": req.get("name", code),
                    "target": target,
                    "actual": cand_lvl,
                    "gap": target - cand_lvl,
                    "priority": priority,
                })
            elif cand_lvl >= target:
                strengths.append({
                    "code": code,
                    "name": req.get("name", code),
                    "target": target,
                    "actual": cand_lvl,
                    "surplus": cand_lvl - target,
                })

        fit_score = (total_fit / weights_sum) * 100 if weights_sum > 0 else 0

        result = {
            "candidateId": candidate_id,
            "jobId": job_id,
            "fitScore": round(fit_score, 1),
            "gaps": gaps,
            "strengths": strengths,
            "recommendation": self._get_recommendation(fit_score),
            "status": "Calculated",
        }

        self.log(f"Fit Score: {result['fitScore']}% | Gaps: {len(gaps)} | Strengths: {len(strengths)}")
        return result

    @staticmethod
    def _get_recommendation(score):
        if score >= 85:
            return "Excellent fit — Sẵn sàng phỏng vấn ngay"
        elif score >= 70:
            return "Good fit — Phù hợp, có thể cải thiện 1-2 mảng"
        elif score >= 50:
            return "Partial fit — Cần đào tạo bổ sung trước khi bố trí"
        else:
            return "Low fit — Không phù hợp vị trí này, đề xuất vị trí khác"
