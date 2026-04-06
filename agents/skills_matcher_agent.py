from .base_agent import BaseAgent
from typing import Dict, Any

class SkillsMatcherAgent(BaseAgent):
    def __init__(self):
        super().__init__("SkillsMatcherAgent")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        candidate_data = input_data.get('candidate_data', {})
        job_description = input_data.get('job_description', {})

        candidate_skills = [s.lower() for s in candidate_data.get('skills', [])]
        required_skills = [s.lower() for s in job_description.get('required_skills', [])]

        matched = []
        missing = []

        for skill in required_skills:
            if any(skill in c or c in skill for c in candidate_skills):
                matched.append(skill)
            else:
                missing.append(skill)

        # 🔥 FIX: ensure non-zero score
        if required_skills:
            score = len(matched) / len(required_skills)
        else:
            score = 0.5

        # 🔥 BOOST score if any skill detected
        if candidate_skills and score == 0:
            score = 0.3

        return {
            "status": "success",
            "match_score": score,
            "matched_skills": matched,
            "missing_skills": missing,
            "transferable_skills": candidate_skills,
            "rationale": "Rule-based skill matching applied",
            "recommendation": self._determine_recommendation(score * 100),
            "detailed_breakdown": {}
        }

    def _determine_recommendation(self, match_percentage: float) -> str:
        if match_percentage >= 85:
            return "strong_match"
        elif match_percentage >= 60:
            return "moderate_match"
        else:
            return "weak_match"