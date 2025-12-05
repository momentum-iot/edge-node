"""Application services for the simplified health bounded context."""
from typing import Dict

from health.domain.services import HeartRateService
from health.infrastructure.repositories import HeartRateRecordRepository


class HeartRateApplicationService:
    """Application service for recording heart rate data."""

    def __init__(self):
        """Initialize the HeartRateApplicationService."""
        self.hr_repository = HeartRateRecordRepository()
        self.hr_service = HeartRateService()

    def record_heart_rate(self, member_id: str, bpm: float) -> Dict:
        """Record a heart rate measurement for a member (no equipment session required).

        Args:
            member_id (str): Member identifier (NFC UID).
            bpm (float): Heart rate in BPM.

        Returns:
            Dict: Saved record details or error.
        """
        try:
            record = self.hr_service.create_record(member_id=member_id, bpm=bpm)
            saved_record = self.hr_repository.save(record)

            return {
                "success": True,
                "record_id": saved_record.id,
                "member_id": saved_record.member_id,
                "bpm": saved_record.bpm,
                "measured_at": saved_record.measured_at.isoformat()
            }
        except ValueError as e:
            return {
                "success": False,
                "error": str(e)
            }
