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

        # 🔥 SKILL SYNONYMS
        synonyms = {
            "ai": ["machine learning", "ml", "deep learning"],
            "ml": ["machine learning", "ai"],
            "python": ["python3", "py"],
            "aws": ["amazon web services", "ec2", "s3"],
            "docker": ["containers"],
            "sql": ["mysql", "postgresql"]
        }

        matched = []
        missing = []

        for req in required_skills:
            matched_flag = False

            for cand in candidate_skills:
                # direct match
                if req in cand or cand in req:
                    matched_flag = True

                # synonym match
                elif req in synonyms and cand in synonyms[req]:
                    matched_flag = True

                elif cand in synonyms and req in synonyms[cand]:
                    matched_flag = True

            if matched_flag:
                matched.append(req)
            else:
                missing.append(req)

        # 🔥 SCORE CALCULATION
        if required_skills:
            score = len(matched) / len(required_skills)
        else:
            score = 0.5

        # 🔥 BOOST if any skills present
        if candidate_skills and score == 0:
            score = 0.3

        return {
            "status": "success",
            "match_score": score,
            "matched_skills": matched,
            "missing_skills": missing,
            "transferable_skills": candidate_skills,
            "rationale": "Enhanced skill + synonym matching",
            "recommendation": self._determine_recommendation(score * 100),
            "detailed_breakdown": {}
        }

    def _determine_recommendation(self, match_percentage: float) -> str:
        if match_percentage >= 80:
            return "strong_match"
        elif match_percentage >= 50:
            return "moderate_match"
        else:
            return "weak_match"