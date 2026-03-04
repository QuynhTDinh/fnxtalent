from base_agent import BaseAgent

class MatchingAgent(BaseAgent):
    def __init__(self, framework_path):
        super().__init__("MatchingAgent", framework_path)
        self.candidate_res = None
        self.jd_reqs = None

    def handle_event(self, event_name, data):
        """Handle incoming events."""
        if event_name == "COMPETENCY_MEASURED":
            self.candidate_res = data
            return self.try_perform_match()
        elif event_name == "REQUIREMENTS_READY":
            self.jd_reqs = data
            return self.try_perform_match()

    def try_perform_match(self):
        if self.candidate_res and self.jd_reqs:
            return self.perform_match()
        return None

    def perform_match(self):
        """Skill: Calculate fit score between candidate and JD requirements."""
        candidate_id = self.candidate_res.get("candidateId")
        job_id = self.jd_reqs.get("job_id")
        
        self.log(f"Performing match for Candidate {candidate_id} and Job {job_id}")
        
        cand_comps = {c['code']: c for c in self.candidate_res.get('competencies', [])}
        required_comps = self.jd_reqs.get('required_competencies', [])
        
        gaps = []
        total_fit = 0
        weights_sum = 0
        
        # Priority-based weights
        priority_weights = {"High": 1.0, "Medium": 0.6, "Low": 0.3}
        
        for req in required_comps:
            code = req['code']
            target = req['target_level']
            priority = req.get('priority', 'Medium')
            weight = priority_weights.get(priority, 0.6)
            
            cand_lvl = cand_comps.get(code, {}).get('level', 0)
            
            # Basic fit: (Candidate Level / Target Level) capped at 1.0
            fit = min(1.0, cand_lvl / target) if target > 0 else 1.0
            
            total_fit += fit * weight
            weights_sum += weight
            
            if cand_lvl < target:
                gaps.append({
                    "code": code,
                    "target": target,
                    "actual": cand_lvl,
                    "gap": target - cand_lvl,
                    "priority": priority
                })
        
        fit_score = (total_fit / weights_sum) * 100 if weights_sum > 0 else 0
        
        result = {
            "candidateId": candidate_id,
            "jobId": job_id,
            "fitScore": round(fit_score, 1),
            "gaps": gaps,
            "status": "Calculated"
        }
        
        self.emit_event("MATCH_COMPLETE", result)
        return result

if __name__ == "__main__":
    # Mock testing the agent
    agent = MatchingAgent("docs/building-21/framework_definition.md")
    
    mock_candidate = {
        "candidateId": "cand_001",
        "competencies": [
            {"code": "HOS.1", "level": 3},
            {"code": "SCI.1", "level": 4}
        ]
    }
    
    mock_jd = {
        "job_id": "job_999",
        "required_competencies": [
            {"code": "HOS.1", "target_level": 4, "priority": "High"},
            {"code": "SCI.1", "target_level": 3, "priority": "Medium"}
        ]
    }
    
    agent.handle_event("COMPETENCY_MEASURED", mock_candidate)
    agent.handle_event("REQUIREMENTS_READY", mock_jd)
