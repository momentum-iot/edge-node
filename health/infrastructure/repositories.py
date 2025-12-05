"""Repository for heart rate record persistence (simplified)."""
from datetime import datetime
from typing import List

from health.domain.entities import HeartRateRecord
from health.infrastructure.models import HeartRateRecord as HeartRateRecordModel


class HeartRateRecordRepository:
    """Repository for managing HeartRateRecord persistence."""

    @staticmethod
    def save(record: HeartRateRecord) -> HeartRateRecord:
        """Persist a heart rate record."""
        record_model = HeartRateRecordModel.create(
            member_id=record.member_id,
            bpm=record.bpm,
            measured_at=record.measured_at,
            created_at=record.created_at or datetime.now(),
        )
        record.id = record_model.id
        return record

    @staticmethod
    def find_by_member_id(member_id: str) -> List[HeartRateRecord]:
        """Return all heart rate records for a member."""
        records = HeartRateRecordModel.select().where(
            HeartRateRecordModel.member_id == member_id
        )
        return [
            HeartRateRecord(
                member_id=r.member_id,
                bpm=r.bpm,
                measured_at=r.measured_at,
                created_at=r.created_at,
                id=r.id,
            )
            for r in records
        ]
