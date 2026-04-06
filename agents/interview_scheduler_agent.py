from agents.base_agent import BaseAgent
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json
from tools.calendar_integration import CalendarService
from tools.email_service import EmailService
from config import config

class InterviewSchedulerAgent(BaseAgent):
    """Agent responsible for scheduling interviews"""
    
    def __init__(self):
        super().__init__("InterviewSchedulerAgent")
        self.calendar_service = CalendarService()
        self.email_service = EmailService(
            smtp_host=config.SMTP_HOST,
            smtp_port=config.SMTP_PORT,
            username=config.SMTP_USER,
            password=config.SMTP_PASSWORD
        )
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Schedule interviews for qualified candidates
        
        Args:
            input_data: Dictionary containing 'candidates' and 'interviewer_calendars'
            
        Returns:
            Dictionary with scheduled interview details
        """
        self.log_info("Starting interview scheduling...")
        
        try:
            candidates = input_data.get('candidates', [])
            interviewer_email = input_data.get('interviewer_email', '')
            interview_duration = input_data.get('duration_minutes', 60)
            
            if not candidates:
                self.log_info("No candidates to schedule")
                return {
                    "status": "success",
                    "scheduled_slots": [],
                    "message": "No candidates provided for scheduling"
                }
            
            scheduled_slots = []
            
            for candidate in candidates:
                try:
                    # Get available slots from calendar
                    available_slots = self._get_available_slots(
                        interviewer_email,
                        days_ahead=14,
                        duration_minutes=interview_duration
                    )
                    
                    if not available_slots:
                        self.log_error(f"No available slots for candidate {candidate.get('name')}")
                        continue
                    
                    # Select best slot (first available)
                    selected_slot = available_slots[0]
                    
                    # Create calendar event
                    event_details = self._create_event_details(
                        candidate=candidate,
                        start_time=selected_slot['start'],
                        end_time=selected_slot['end'],
                        interviewer_email=interviewer_email
                    )
                    
                    # Create event in calendar
                    calendar_event = self.calendar_service.create_event(
                        calendar_id=interviewer_email,
                        event_details=event_details
                    )
                    
                    # Send email notification
                    self._send_interview_invitation(
                        candidate=candidate,
                        event_details=event_details
                    )
                    
                    scheduled_slots.append({
                        "candidate_id": candidate.get('id'),
                        "candidate_name": candidate.get('name'),
                        "candidate_email": candidate.get('email'),
                        "start_time": selected_slot['start'].isoformat(),
                        "end_time": selected_slot['end'].isoformat(),
                        "calendar_event_id": calendar_event.get('id'),
                        "status": "scheduled"
                    })
                    
                    self.log_info(f"Successfully scheduled interview for {candidate.get('name')}")
                    
                except Exception as e:
                    self.log_error(f"Failed to schedule for candidate {candidate.get('name')}: {str(e)}")
                    continue
            
            return {
                "status": "success",
                "scheduled_slots": scheduled_slots,
                "total_scheduled": len(scheduled_slots),
                "total_attempted": len(candidates)
            }
            
        except Exception as e:
            self.log_error(f"Error in interview scheduling: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "scheduled_slots": []
            }
    
    def _get_available_slots(self, 
                            calendar_id: str, 
                            days_ahead: int = 14,
                            duration_minutes: int = 60) -> List[Dict[str, datetime]]:
        """Get available time slots from calendar"""
        try:
            start_date = datetime.now()
            end_date = start_date + timedelta(days=days_ahead)
            
            # Get available slots from calendar service
            available_slots = self.calendar_service.get_available_slots(
                calendar_id=calendar_id,
                start_date=start_date,
                end_date=end_date,
                duration_minutes=duration_minutes
            )
            
            return available_slots
            
        except Exception as e:
            self.log_error(f"Error getting available slots: {str(e)}")
            return []
    
    def _create_event_details(self,
                             candidate: Dict[str, Any],
                             start_time: datetime,
                             end_time: datetime,
                             interviewer_email: str) -> Dict[str, Any]:
        """Create event details for calendar"""
        return {
            "summary": f"Interview with {candidate.get('name')}",
            "description": f"""
Interview scheduled with candidate {candidate.get('name')}

Position: {candidate.get('position', 'N/A')}
Overall Match Score: {candidate.get('overall_score', 'N/A')}%
Skills Match: {candidate.get('skills_match_score', 'N/A')}%
Cultural Fit: {candidate.get('cultural_fit_score', 'N/A')}%

Candidate Email: {candidate.get('email')}
Candidate Phone: {candidate.get('phone', 'N/A')}
            """.strip(),
            "start": start_time,
            "end": end_time,
            "attendees": [
                {"email": interviewer_email},
                {"email": candidate.get('email')}
            ],
            "conferenceData": {
                "createRequest": {
                    "requestId": f"interview-{candidate.get('id')}-{int(start_time.timestamp())}"
                }
            }
        }
    
    def _send_interview_invitation(self,
                                   candidate: Dict[str, Any],
                                   event_details: Dict[str, Any]):
        """Send interview invitation email to candidate"""
        try:
            subject = f"Interview Invitation - {event_details['summary']}"
            
            body = f"""
Dear {candidate.get('name')},

We are pleased to invite you for an interview for the position you applied for.

Interview Details:
Date & Time: {event_details['start'].strftime('%A, %B %d, %Y at %I:%M %p')}
Duration: {(event_details['end'] - event_details['start']).seconds // 60} minutes

A calendar invitation has been sent to your email. Please accept the invitation to confirm your attendance.

We look forward to speaking with you!

Best regards,
Recruitment Team
            """.strip()
            
            self.email_service.send_email(
                to_email=candidate.get('email'),
                subject=subject,
                body=body
            )
            
            self.log_info(f"Interview invitation sent to {candidate.get('email')}")
            
        except Exception as e:
            self.log_error(f"Failed to send invitation email: {str(e)}")