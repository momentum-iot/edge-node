"""
Repository for equipment and heart rate record persistence.

Handles saving equipment, sessions, and heart rate records to the database using Peewee ORM models.
"""
from datetime import datetime
from typing import Optional, List
import peewee

from health.domain.entities import Equipment, EquipmentSession, HeartRateRecord
from health.infrastructure.models import (
    Equipment as EquipmentModel,
    EquipmentSession as EquipmentSessionModel,
    HeartRateRecord as HeartRateRecordModel
)


class EquipmentRepository:
    """
    Repository for managing Equipment persistence.
    """

    @staticmethod
    def save(equipment: Equipment) -> Equipment:
        """
        Save an Equipment entity to the database.
        
        Args:
            equipment (Equipment): The equipment to save.
            
        Returns:
            Equipment: The saved equipment with assigned ID.
        """
        if equipment.id:
            # Update existing
            EquipmentModel.update(
                name=equipment.name,
                equipment_type=equipment.equipment_type
            ).where(EquipmentModel.id == equipment.id).execute()
            return equipment
        else:
            # Create new
            eq_model = EquipmentModel.create(
                name=equipment.name,
                equipment_type=equipment.equipment_type,
                created_at=equipment.created_at
            )
            equipment.id = eq_model.id
            return equipment

    @staticmethod
    def find_by_id(equipment_id: int) -> Optional[Equipment]:
        """
        Find equipment by ID.
        
        Args:
            equipment_id (int): Equipment ID.
            
        Returns:
            Optional[Equipment]: Equipment entity if found, None otherwise.
        """
        try:
            eq = EquipmentModel.get(EquipmentModel.id == equipment_id)
            return Equipment(
                name=eq.name,
                equipment_type=eq.equipment_type,
                created_at=eq.created_at,
                id=eq.id
            )
        except peewee.DoesNotExist:
            return None

    @staticmethod
    def get_or_create_test_equipment() -> Equipment:
        """Get or create test equipment for development.

        Returns:
            Equipment: Test equipment entity.
        """
        eq_model, _ = EquipmentModel.get_or_create(
            name="Test Treadmill",
            defaults={
                "equipment_type": "treadmill",
                "created_at": datetime.now()
            }
        )
        return Equipment(
            name=eq_model.name,
            equipment_type=eq_model.equipment_type,
            created_at=eq_model.created_at,
            id=eq_model.id
        )


class EquipmentSessionRepository:
    """
    Repository for managing EquipmentSession persistence.
    """

    @staticmethod
    def save(session: EquipmentSession) -> EquipmentSession:
        """
        Save an EquipmentSession entity to the database.
        
        Args:
            session (EquipmentSession): The session to save.
            
        Returns:
            EquipmentSession: The saved session with assigned ID.
        """
        if session.id:
            # Update existing (for ending session)
            EquipmentSessionModel.update(
                end_time=session.end_time
            ).where(EquipmentSessionModel.id == session.id).execute()
            return session
        else:
            # Create new session
            session_model = EquipmentSessionModel.create(
                member_id=session.member_id,
                equipment_id=session.equipment_id,
                start_time=session.start_time,
                end_time=session.end_time,
                created_at=session.created_at
            )
            session.id = session_model.id
            return session

    @staticmethod
    def find_active_by_member_id(member_id: int) -> Optional[EquipmentSession]:
        """
        Find an active session (no end_time) for a member.
        
        Args:
            member_id (int): Member ID.
            
        Returns:
            Optional[EquipmentSession]: Active session if found, None otherwise.
        """
        try:
            session = EquipmentSessionModel.get(
                (EquipmentSessionModel.member_id == member_id) &
                (EquipmentSessionModel.end_time.is_null())
            )
            return EquipmentSession(
                member_id=session.member_id,
                equipment_id=session.equipment_id.id,
                start_time=session.start_time,
                end_time=session.end_time,
                created_at=session.created_at,
                id=session.id
            )
        except peewee.DoesNotExist:
            return None

    @staticmethod
    def find_by_id(session_id: int) -> Optional[EquipmentSession]:
        """
        Find a session by ID.
        
        Args:
            session_id (int): Session ID.
            
        Returns:
            Optional[EquipmentSession]: Session entity if found, None otherwise.
        """
        try:
            session = EquipmentSessionModel.get(EquipmentSessionModel.id == session_id)
            return EquipmentSession(
                member_id=session.member_id,
                equipment_id=session.equipment_id.id,
                start_time=session.start_time,
                end_time=session.end_time,
                created_at=session.created_at,
                id=session.id
            )
        except peewee.DoesNotExist:
            return None


class HeartRateRecordRepository:
    """
    Repository for managing HeartRateRecord persistence.
    """

    @staticmethod
    def save(record: HeartRateRecord) -> HeartRateRecord:
        """
        Save a HeartRateRecord entity to the database.
        
        Args:
            record (HeartRateRecord): The heart rate record to save.
            
        Returns:
            HeartRateRecord: The saved record with assigned ID.
        """
        record_model = HeartRateRecordModel.create(
            session_id=record.session_id,
            member_id=record.member_id,
            bpm=record.bpm,
            measured_at=record.measured_at,
            created_at=record.created_at
        )
        record.id = record_model.id
        return record

    @staticmethod
    def find_by_session_id(session_id: int) -> List[HeartRateRecord]:
        """
        Find all heart rate records for a session.
        
        Args:
            session_id (int): Session ID.
            
        Returns:
            List[HeartRateRecord]: List of heart rate records.
        """
        records = HeartRateRecordModel.select().where(
            HeartRateRecordModel.session_id == session_id
        )
        return [
            HeartRateRecord(
                session_id=r.session_id.id,
                member_id=r.member_id,
                bpm=r.bpm,
                measured_at=r.measured_at,
                created_at=r.created_at,
                id=r.id
            )
            for r in records
        ]

