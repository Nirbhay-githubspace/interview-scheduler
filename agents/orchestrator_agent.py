from .base_agent import BaseAgent
from .resume_parser_agent import ResumeParserAgent
from .skills_matcher_agent import SkillsMatcherAgent
from .cultural_fit_agent import CulturalFitAgent
from .interview_scheduler_agent import InterviewSchedulerAgent
from typing import Dict, Any, List
import asyncio
from config import config


class OrchestratorAgent(BaseAgent):
    def __init__(self):
        super().__init__("OrchestratorAgent")
        self.resume_parser = ResumeParserAgent()
        self.skills_matcher = SkillsMatcherAgent()
        self.cultural_fit = CulturalFitAgent()
        self.interview_scheduler = InterviewSchedulerAgent()

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            resumes = input_data.get('resumes', [])
            job_description = input_data.get('job_description', {})
            company_culture = input_data.get('company_culture', {})
            interviewer_email = input_data.get('interviewer_email', '')

            if not resumes:
                return {"status": "error", "message": "No resumes provided", "ranked_candidates": []}

            if not job_description:
                return {"status": "error", "message": "No job description provided", "ranked_candidates": []}

            # =========================
            # PHASE 1: PARSE
            # =========================
            parsed_candidates = await self._parse_resumes_parallel(resumes)

            valid_candidates = []
            for c in parsed_candidates:
                if c.get('status') == 'success':
                    valid_candidates.append(c)
                else:
                    idx = c.get("resume_index", 0)
                    resume_data = resumes[idx]

                    fallback_candidate = {
                        "status": "success",
                        "resume_index": idx,
                        "id": f"fallback_{idx}",
                        "candidate_data": {
                            "personal_info": {
                                "name": resume_data.get("filename", f"Candidate {idx+1}"),
                                "email": ""
                            },
                            "work_experience": [],
                            "skills": []
                        }
                    }

                    valid_candidates.append(fallback_candidate)

            # =========================
            # PHASE 2: EVALUATE
            # =========================
            evaluated_candidates = await self._evaluate_candidates_parallel(
                valid_candidates,
                job_description,
                company_culture
            )

            # =========================
            # PHASE 3: RANK
            # =========================
            ranked_candidates = self._rank_candidates(evaluated_candidates)

            # =========================
            # PHASE 4: FILTER
            # =========================
            qualified_candidates = self._filter_qualified_candidates(ranked_candidates)

            scheduling_result = {"scheduled_slots": []}
            if qualified_candidates and interviewer_email:
                scheduling_result = await self.interview_scheduler.process({
                    "candidates": qualified_candidates,
                    "interviewer_email": interviewer_email
                })

            return {
                "status": "success",
                "ranked_candidates": ranked_candidates,
                "processing_summary": {
                    "total_resumes": len(resumes),
                    "successfully_parsed": len(valid_candidates),
                    "qualified_candidates": len(qualified_candidates),
                    "interviews_scheduled": len(scheduling_result.get('scheduled_slots', []))
                },
                "scheduled_interviews": scheduling_result.get('scheduled_slots', [])
            }

        except Exception as e:
            return {"status": "error", "message": str(e), "ranked_candidates": []}

    async def _parse_resumes_parallel(self, resumes):
        tasks = [self._parse_single_resume(resume, idx) for idx, resume in enumerate(resumes)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        parsed = []
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                parsed.append({"status": "error", "resume_index": idx})
            else:
                parsed.append({**result, "resume_index": idx, "id": f"candidate_{idx}"})

        return parsed

    async def _parse_single_resume(self, resume, index):
        return await self.resume_parser.process(resume)

    async def _evaluate_candidates_parallel(self, candidates, job_description, company_culture):
        tasks = [self._evaluate_single_candidate(c, job_description, company_culture) for c in candidates]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if not isinstance(r, Exception)]

    async def _evaluate_single_candidate(self, candidate, job_description, company_culture):
        candidate_data = candidate.get('candidate_data', {})

        skills_task = self.skills_matcher.process({
            "candidate_data": candidate_data,
            "job_description": job_description
        })

        cultural_task = self.cultural_fit.process({
            "candidate_data": candidate_data,
            "company_culture": company_culture,
            "job_description": job_description
        })

        skills_result, cultural_result = await asyncio.gather(skills_task, cultural_task)

        return {
            "id": candidate.get('id'),
            "candidate_data": candidate_data,
            "skills_evaluation": skills_result,
            "cultural_evaluation": cultural_result
        }

    def _rank_candidates(self, candidates):
        ranked = []

        for candidate in candidates:
            skills_eval = candidate.get('skills_evaluation', {})
            cultural_eval = candidate.get('cultural_evaluation', {})
            data = candidate.get('candidate_data', {})

            # ✅ DEBUG
            print("SKILLS:", skills_eval)
            print("CULTURE:", cultural_eval)

            skills_score = skills_eval.get('match_score', 0)
            cultural_score = cultural_eval.get('cultural_fit_score', 0.5)

            exp_score = min(len(data.get('work_experience', [])) * 2 / 10, 1.0)

            overall_score = (
                skills_score * config.SKILLS_WEIGHT +
                cultural_score * config.CULTURAL_FIT_WEIGHT +
                exp_score * config.EXPERIENCE_WEIGHT
            )

            # 🔥 FIX: avoid 0 score collapse
            if overall_score == 0:
                overall_score = 0.3

            ranked.append({
                "id": candidate.get('id'),
                "candidate_data": data,
                "name": data.get('personal_info', {}).get('name', 'Unknown'),
                "email": data.get('personal_info', {}).get('email', ''),
                "overall_score": round(overall_score * 100, 2),
                "skills_match_score": round(skills_score * 100, 2),
                "cultural_fit_score": round(cultural_score * 100, 2),
                "tier": self._determine_tier(overall_score),
                "matched_skills": skills_eval.get('matched_skills', [])
            })

        ranked.sort(key=lambda x: x['overall_score'], reverse=True)
        return ranked

    def _determine_tier(self, score):
        if score * 100 >= 85:
            return "strong_match"
        elif score * 100 >= 70:
            return "moderate_match"
        return "weak_match"

    def _filter_qualified_candidates(self, candidates):
        return candidates[:max(1, len(candidates)//5)]