from .base_agent import BaseAgent
from typing import Dict, Any

class SkillsMatcherAgent(BaseAgent):

    def __init__(self):
        super().__init__("SkillsMatcherAgent")

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        candidate_data = input_data.get("candidate_data", {})
        job_description = input_data.get("job_description", {})

        candidate_skills = [s.lower() for s in candidate_data.get("skills", [])]
        required_skills = [s.lower() for s in job_description.get("required_skills", [])]

        print("CANDIDATE SKILLS:", candidate_skills)
        print("REQUIRED SKILLS:", required_skills)

        matched = []
        missing = []

        for req in required_skills:
            if any(req in skill or skill in req for skill in candidate_skills):
                matched.append(req)
            else:
                missing.append(req)

        # 🔥 CORE FIX
        if required_skills:
            score = len(matched) / len(required_skills)
        else:
            score = 0.5

        # 🔥 SAFETY BOOST (CRITICAL)
        if score == 0 and candidate_skills:
            score = 0.3

        print("MATCHED:", matched)
        print("FINAL SCORE:", score)

        return {
            "status": "success",
            "match_score": score,   # 🚨 MUST BE THIS KEY
            "matched_skills": matched,
            "missing_skills": missing,
            "rationale": "Basic matching applied",
            "recommendation": "weak_match"
        }