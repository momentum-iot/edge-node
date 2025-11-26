"""Application services for the Equipment Usage bounded context."""
from datetime import datetime
from typing import Optional, Dict

from health.domain.entities import Equipment, EquipmentSession, HeartRateRecord
from health.domain.services import EquipmentService, EquipmentSessionService, HeartRateService
from health.infrastructure.repositories import EquipmentRepository, EquipmentSessionRepository, HeartRateRecordRepository
from iam.infrastructure.repositories import MemberRepository, CheckInRepository


class EquipmentSessionApplicationService:
    """Application service for managing equipment usage sessions."""

    def __init__(self):
        """Initialize the EquipmentSessionApplicationService."""
        self.session_repository = EquipmentSessionRepository()
        self.equipment_repository = EquipmentRepository()
        self.member_repository = MemberRepository()
        self.check_in_repository = CheckInRepository()
        self.session_service = EquipmentSessionService()

    def start_equipment_session(self, member_id: int, equipment_id: int) -> Dict:
        """Start a new equipment usage session.

        Args:
            member_id (int): Member ID.
            equipment_id (int): Equipment ID.

        Returns:
            Dict: Session details or error.
        """
        # Validate member exists
        member = self.member_repository.find_by_nfc_uid(str(member_id))  # Simplified for now
        if not member:
            # Try to find by checking active check-in
            active_check_in = self.check_in_repository.find_active_by_member_id(member_id)
            if not active_check_in:
                return {
                    "success": False,
                    "error": "Member not checked in to gym"
                }

        # Validate equipment exists
        equipment = self.equipment_repository.find_by_id(equipment_id)
        if not equipment:
            return {
                "success": False,
                "error": "Equipment not found"
            }

        # Check if member already has an active session
        active_session = self.session_repository.find_active_by_member_id(member_id)
        if active_session:
            return {
                "success": False,
                "error": "Member already has an active equipment session",
                "active_session_id": active_session.id
            }

        # Create new session
        session = self.session_service.start_session(member_id, equipment_id)
        saved_session = self.session_repository.save(session)

        return {
            "success": True,
            "session_id": saved_session.id,
            "member_id": saved_session.member_id,
            "equipment_id": saved_session.equipment_id,
            "start_time": saved_session.start_time.isoformat()
        }

    def end_equipment_session(self, member_id: int) -> Dict:
        """End the active equipment session for a member.

        Args:
            member_id (int): Member ID.

        Returns:
            Dict: Updated session details or error.
        """
        # Find active session
        active_session = self.session_repository.find_active_by_member_id(member_id)
        if not active_session:
            return {
                "success": False,
                "error": "No active session found for member"
            }

        # End session
        ended_session = self.session_service.end_session(active_session)
        saved_session = self.session_repository.save(ended_session)

        return {
            "success": True,
            "session_id": saved_session.id,
            "member_id": saved_session.member_id,
            "equipment_id": saved_session.equipment_id,
            "start_time": saved_session.start_time.isoformat(),
            "end_time": saved_session.end_time.isoformat()
        }

    def get_or_create_test_equipment(self) -> Equipment:
        """Get or create test equipment for development.

        Returns:
            Equipment: Test equipment entity.
        """
        return self.equipment_repository.get_or_create_test_equipment()


class HeartRateApplicationService:
    """Application service for recording heart rate data."""

    def __init__(self):
        """Initialize the HeartRateApplicationService."""
        self.hr_repository = HeartRateRecordRepository()
        self.session_repository = EquipmentSessionRepository()
        self.hr_service = HeartRateService()

    def record_heart_rate(self, session_id: int, member_id: int, bpm: float) -> Dict:
        """Record a heart rate measurement.

        Args:
            session_id (int): Equipment session ID.
            member_id (int): Member ID.
            bpm (float): Heart rate in BPM.

        Returns:
            Dict: Saved record details or error.
        """
        # Validate session exists and is active
        session = self.session_repository.find_by_id(session_id)
        if not session:
            return {
                "success": False,
                "error": "Session not found"
            }

        if not session.is_active():
            return {
                "success": False,
                "error": "Session has ended"
            }

        if session.member_id != member_id:
            return {
                "success": False,
                "error": "Member ID does not match session"
            }

        try:
            # Create heart rate record
            record = self.hr_service.create_record(session_id, member_id, bpm)
            saved_record = self.hr_repository.save(record)

            return {
                "success": True,
                "record_id": saved_record.id,
                "session_id": saved_record.session_id,
                "member_id": saved_record.member_id,
                "bpm": saved_record.bpm,
                "measured_at": saved_record.measured_at.isoformat()
            }
        except ValueError as e:
            return {
                "success": False,
                "error": str(e)
            }