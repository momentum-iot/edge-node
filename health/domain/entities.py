"""Domain entities for the Equipment Usage bounded context."""
from datetime import datetime
from typing import Optional


class Equipment:
    """Represents a gym equipment/machine entity.

    Attributes:
        id (int): Unique identifier for the equipment.
        name (str): Equipment name (e.g., "Treadmill 1", "Bike 2").
        equipment_type (str): Type of equipment (treadmill, bike, bench, etc.).
        created_at (datetime): Timestamp when the equipment was registered.
    """

    def __init__(self, name: str, equipment_type: str, created_at: datetime, id: Optional[int] = None):
        """Initialize an Equipment instance.

        Args:
            name (str): Equipment name.
            equipment_type (str): Type of equipment.
            created_at (datetime): Registration timestamp.
            id (int, optional): Equipment ID.
        """
        self.id = id
        self.name = name
        self.equipment_type = equipment_type
        self.created_at = created_at


class EquipmentSession:
    """Represents a usage session of gym equipment by a member.

    Attributes:
        id (int): Unique identifier for the session.
        member_id (int): ID of the member using the equipment.
        equipment_id (int): ID of the equipment being used.
        start_time (datetime): Session start timestamp.
        end_time (datetime): Session end timestamp (None if ongoing).
        created_at (datetime): Record creation timestamp.
    """

    def __init__(self, member_id: int, equipment_id: int, start_time: datetime,
                 end_time: Optional[datetime] = None,
                 created_at: Optional[datetime] = None, id: Optional[int] = None):
        """Initialize an EquipmentSession instance.

        Args:
            member_id (int): Member ID.
            equipment_id (int): Equipment ID.
            start_time (datetime): Start timestamp.
            end_time (datetime, optional): End timestamp.
            created_at (datetime, optional): Record creation timestamp.
            id (int, optional): Session ID.
        """
        self.id = id
        self.member_id = member_id
        self.equipment_id = equipment_id
        self.start_time = start_time
        self.end_time = end_time
        self.created_at = created_at or datetime.now()

    def is_active(self) -> bool:
        """Check if this session is still active.

        Returns:
            bool: True if session hasn't ended yet.
        """
        return self.end_time is None


class HeartRateRecord:
    """Represents a heart rate measurement during equipment usage.

    Attributes:
        id (int): Unique identifier for the record.
        session_id (int): ID of the equipment session.
        member_id (int): ID of the member.
        bpm (float): Beats per minute (heart rate).
        measured_at (datetime): Timestamp when the measurement was taken.
        created_at (datetime): Record creation timestamp.
    """

    def __init__(self, session_id: int, member_id: int, bpm: float, 
                 measured_at: datetime, created_at: Optional[datetime] = None, 
                 id: Optional[int] = None):
        """Initialize a HeartRateRecord instance.

        Args:
            session_id (int): Session ID.
            member_id (int): Member ID.
            bpm (float): Heart rate in beats per minute.
            measured_at (datetime): Measurement timestamp.
            created_at (datetime, optional): Record creation timestamp.
            id (int, optional): Record identifier.
        """
        self.id = id
        self.session_id = session_id
        self.member_id = member_id
        self.bpm = bpm
        self.measured_at = measured_at
        self.created_at = created_at or datetime.now()