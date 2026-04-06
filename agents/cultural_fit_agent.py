from .base_agent import BaseAgent
from typing import Dict, Any

class CulturalFitAgent(BaseAgent):
    def __init__(self):
        super().__init__("CulturalFitAgent")

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        candidate = input_data.get("candidate_data", {})
        skills = candidate.get("skills", [])

        # 🔥 SIMPLE LOGIC
        if len(skills) >= 5:
            score = 0.7
        elif len(skills) >= 3:
            score = 0.5
        else:
            score = 0.3

        return {
            "status": "success",
            "cultural_fit_score": score,
            "rationale": "Skill diversity based cultural fit",
            "dimensional_scores": {}
        }