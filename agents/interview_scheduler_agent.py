from agents.base_agent import BaseAgent
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json
from tools.email_service import EmailService
from config import config


class InterviewSchedulerAgent(BaseAgent):
    """Agent responsible for scheduling interviews (Calendar Disabled Version)"""

    def __init__(self):
        super().__init__("InterviewSchedulerAgent")

        # 🔥 Calendar completely disabled
        self.calendar_service = None

        # Email service (optional, will not break app if not configured)
        self.email_service = EmailService(
            smtp_host=config.SMTP_HOST,
            smtp_port=config.SMTP_PORT,
            username=config.SMTP_USER,
            password=config.SMTP_PASSWORD
        )

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Schedule interviews for qualified candidates
        (Currently disabled for deployment safety)
        """

        self.log_info("Starting interview scheduling...")

        # 🔥 HARD DISABLE — no calendar required
        candidates = input_data.get('candidates', [])

        return {
            "status": "success",
            "scheduled_slots": [],
            "total_scheduled": 0,
            "total_attempted": len(candidates),
            "message": "Interview scheduling skipped (calendar integration disabled)"
        }

    # 👇 Keep helper methods (not used, but safe to keep)

    def _get_available_slots(
        self,
        calendar_id: str,
        days_ahead: int = 14,
        duration_minutes: int = 60
    ) -> List[Dict[str, datetime]]:
        """Get available time slots (disabled)"""
        return []

    def _create_event_details(
        self,
        candidate: Dict[str, Any],
        start_time: datetime,
        end_time: datetime,
        interviewer_email: str
    ) -> Dict[str, Any]:
        """Create event details (unused)"""
        return {}

    def _send_interview_invitation(
        self,
        candidate: Dict[str, Any],
        event_details: Dict[str, Any]
    ):
        """Send interview email (optional, safe fallback)"""
        try:
            subject = "Interview Invitation"

            body = f"""
Dear {candidate.get('name')},

Your profile has been shortlisted. We will contact you shortly for further steps.

Best regards,
Recruitment Team
            """.strip()

            self.email_service.send_email(
                to_email=candidate.get('email'),
                subject=subject,
                body=body
            )

            self.log_info(f"Email sent to {candidate.get('email')}")

        except Exception as e:
            self.log_error(f"Email sending failed: {str(e)}")