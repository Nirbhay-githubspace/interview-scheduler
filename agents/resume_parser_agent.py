from .base_agent import BaseAgent
from typing import Dict, Any
import re

class ResumeParserAgent(BaseAgent):
    def __init__(self):
        super().__init__("ResumeParserAgent")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        print("🔥 PARSER RUNNING 🔥")

        resume_content = input_data.get('resume_content', '')

        if not resume_content:
            return self._fallback_response()

        # 🔥 DIRECT EXTRACTION (NO AI)
        name = self._extract_name(resume_content)
        email = self._extract_email(resume_content)
        skills = self._extract_skills(resume_content)

        candidate_data = {
            "personal_info": {
                "name": name,
                "email": email,
                "phone": ""
            },
            "work_experience": [],
            "education": [],
            "skills": skills
        }

        return {
            "status": "success",
            "candidate_data": candidate_data,
            "confidence_scores": {
                "personal_info": 0.8,
                "skills": 0.7
            }
        }

    # =========================
    # HELPERS
    # =========================

    def _extract_email(self, text: str) -> str:
        match = re.search(r'[\w\.-]+@[\w\.-]+', text)
        return match.group(0) if match else ""

    def _extract_name(self, text: str) -> str:
        lines = text.split("\n")

        for line in lines[:10]:
            clean = line.strip()

            if "@" in clean or "email" in clean.lower():
                continue

            words = clean.split()

            if 1 < len(words) <= 3 and all(w.isalpha() for w in words):
                return clean

        return "Candidate"

    def _extract_skills(self, text: str) -> list:
        common_skills = [
            "python", "java", "aws", "docker", "ml", "ai",
            "react", "sql", "tensorflow", "pandas"
        ]

        found = []
        text_lower = text.lower()

        for skill in common_skills:
            if skill in text_lower:
                found.append(skill.capitalize())

        return found

    def _fallback_response(self):
        return {
            "status": "success",
            "candidate_data": {
                "personal_info": {
                    "name": "Candidate",
                    "email": "",
                    "phone": ""
                },
                "work_experience": [],
                "education": [],
                "skills": []
            },
            "confidence_scores": {}
        }