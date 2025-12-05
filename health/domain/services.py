"""Domain services for the simplified health bounded context."""
from datetime import datetime
from health.domain.entities import HeartRateRecord


class HeartRateService:
    """Service for managing heart rate records."""

    def __init__(self):
        """Initialize the HeartRateService."""

    @staticmethod
    def create_record(member_id: str, bpm: float, measured_at: datetime = None) -> HeartRateRecord:
        """Create a new heart rate record.

        Args:
            member_id (str): Member ID / NFC UID.
            bpm (float): Heart rate in beats per minute.
            measured_at (datetime, optional): Measurement timestamp.

        Returns:
            HeartRateRecord: The created heart rate record entity.

        Raises:
            ValueError: If BPM is invalid (not 30–220).
        """
        try:
            bpm = float(bpm)
            if not (30 <= bpm <= 220):
                raise ValueError("Invalid BPM value: must be between 30 and 220")
        except (ValueError, TypeError):
            raise ValueError("Invalid BPM format")

        measured_at = measured_at or datetime.now()

        return HeartRateRecord(
            member_id=str(member_id),
            bpm=bpm,
            measured_at=measured_at
        )
