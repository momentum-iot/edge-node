"""Domain services for the Equipment Usage bounded context."""
from datetime import datetime
from health.domain.entities import Equipment, EquipmentSession, HeartRateRecord


class EquipmentService:
    """Service for managing gym equipment."""

    def __init__(self):
        """Initialize the EquipmentService."""

    @staticmethod
    def create_equipment(name: str, equipment_type: str) -> Equipment:
        """Create a new equipment entity.

        Args:
            name (str): Equipment name.
            equipment_type (str): Type of equipment.

        Returns:
            Equipment: The created equipment entity.
        """
        return Equipment(name=name, equipment_type=equipment_type, created_at=datetime.now())


class EquipmentSessionService:
    """Service for managing equipment usage sessions."""

    def __init__(self):
        """Initialize the EquipmentSessionService."""

    @staticmethod
    def start_session(member_id: int, equipment_id: int) -> EquipmentSession:
        """Start a new equipment usage session.

        Args:
            member_id (int): ID of the member.
            equipment_id (int): ID of the equipment.

        Returns:
            EquipmentSession: The created session entity.
        """
        return EquipmentSession(
            member_id=member_id,
            equipment_id=equipment_id,
            start_time=datetime.now()
        )

    @staticmethod
    def end_session(session: EquipmentSession) -> EquipmentSession:
        """End an equipment usage session.

        Args:
            session (EquipmentSession): The session to end.

        Returns:
            EquipmentSession: The updated session entity.
        """
        session.end_time = datetime.now()
        return session


class HeartRateService:
    """Service for managing heart rate records."""

    def __init__(self):
        """Initialize the HeartRateService."""

    @staticmethod
    def create_record(session_id: int, member_id: int, bpm: float, measured_at: datetime = None) -> HeartRateRecord:
        """Create a new heart rate record.

        Args:
            session_id (int): Session ID.
            member_id (int): Member ID.
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

        if not measured_at:
            measured_at = datetime.now()

        return HeartRateRecord(
            session_id=session_id,
            member_id=member_id,
            bpm=bpm,
            measured_at=measured_at
        )
