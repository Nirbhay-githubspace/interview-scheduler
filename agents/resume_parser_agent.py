from .base_agent import BaseAgent
from typing import Dict, Any
import json
import re
from prompts.resume_parser_prompts import (
    RESUME_PARSER_SYSTEM_PROMPT,
    RESUME_PARSER_USER_PROMPT
)

class ResumeParserAgent(BaseAgent):
    """Agent responsible for parsing resumes and extracting structured data"""
    
    def __init__(self):
        super().__init__("ResumeParserAgent")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        self.log_info("Starting resume parsing...")
        
        try:
            resume_content = input_data.get('resume_content', '')
            
            if not resume_content:
                return self._fallback_response("Unknown Candidate", resume_content)

            prompt = RESUME_PARSER_USER_PROMPT.format(resume_content=resume_content)

            response = await self._generate_response(
                prompt=prompt,
                system_instruction=RESUME_PARSER_SYSTEM_PROMPT,
                temperature=0.3
            )

            # Clean markdown formatting
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()

            try:
                candidate_data = json.loads(response)

                # 🔥 FORCE CLEAN NAME FIX
                raw_name = candidate_data.get("personal_info", {}).get("name", "")

                if not raw_name or "@" in raw_name or "email" in raw_name.lower():
                    clean_name = self._extract_name(resume_content)
                    candidate_data.setdefault("personal_info", {})["name"] = clean_name

                # 🔥 ENSURE EMAIL EXISTS
                if not candidate_data.get("personal_info", {}).get("email"):
                    candidate_data["personal_info"]["email"] = self._extract_email(resume_content)

                return {
                    "status": "success",
                    "candidate_data": candidate_data,
                    "confidence_scores": self._calculate_confidence_scores(candidate_data)
                }

            except Exception as e:
                self.log_warning(f"JSON parsing failed, using fallback: {str(e)}")
                return self._fallback_from_text(resume_content)

        except Exception as e:
            self.log_error(f"Error in resume parsing: {str(e)}")
            return self._fallback_from_text(resume_content)

    # =========================
    # 🔥 FALLBACK METHODS
    # =========================

    def _fallback_from_text(self, text: str) -> Dict[str, Any]:
        name = self._extract_name(text)
        email = self._extract_email(text)

        candidate_data = {
            "personal_info": {
                "name": name,
                "email": email,
                "phone": ""
            },
            "work_experience": [],
            "education": [],
            "skills": self._extract_skills(text)
        }

        return {
            "status": "success",
            "candidate_data": candidate_data,
            "confidence_scores": {
                "personal_info": 0.7,
                "skills": 0.6
            }
        }

    def _fallback_response(self, name: str, text: str) -> Dict[str, Any]:
        return {
            "status": "success",
            "candidate_data": {
                "personal_info": {
                    "name": name,
                    "email": "",
                    "phone": ""
                },
                "work_experience": [],
                "education": [],
                "skills": []
            },
            "confidence_scores": {}
        }

    # =========================
    # 🔥 EXTRACTION HELPERS
    # =========================

    def _extract_email(self, text: str) -> str:
        match = re.search(r'[\w\.-]+@[\w\.-]+', text)
        return match.group(0) if match else ""

    def _extract_name(self, text: str) -> str:
        lines = text.split("\n")

        for line in lines[:10]:
            clean = line.strip()

            # skip emails / labels
            if "@" in clean or "email" in clean.lower():
                continue

            words = clean.split()

            if 1 < len(words) <= 3 and all(w.isalpha() for w in words):
                return clean

        return "Candidate"

    def _extract_skills(self, text: str) -> list:
        common_skills = [
            "python", "java", "aws", "docker", "ml", "ai",
            "react", "sql", "tensorflow", "pandas", "javascript"
        ]

        found = []
        text_lower = text.lower()

        for skill in common_skills:
            if skill in text_lower:
                found.append(skill.capitalize())

        return found

    def _calculate_confidence_scores(self, candidate_data: Dict[str, Any]) -> Dict[str, float]:
        scores = {}

        if candidate_data.get('personal_info'):
            personal = candidate_data['personal_info']
            fields = ['name', 'email']
            present = sum(1 for f in fields if personal.get(f))
            scores['personal_info'] = present / len(fields)

        scores['skills'] = 1.0 if candidate_data.get('skills') else 0.5

        return scores