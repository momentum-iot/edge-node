"""
Peewee ORM models for equipment usage tracking.

Defines database table structures for equipment, sessions, and heart rate records.
"""
from peewee import Model, AutoField, FloatField, CharField, DateTimeField, IntegerField, ForeignKeyField
from shared.infrastructure.database import db


class Equipment(Model):
    """
    ORM model for the equipment table.
    Represents a gym machine or equipment.
    """
    id = AutoField()
    name = CharField()
    equipment_type = CharField()
    created_at = DateTimeField()

    class Meta:
        database = db
        table_name = 'equipment'


class EquipmentSession(Model):
    """
    ORM model for the equipment_sessions table.
    Represents a member's usage session of a piece of equipment.
    """
    id = AutoField()
    member_id = IntegerField()
    equipment_id = ForeignKeyField(Equipment, backref='sessions', column_name='equipment_id')
    start_time = DateTimeField()
    end_time = DateTimeField(null=True)
    created_at = DateTimeField()

    class Meta:
        database = db
        table_name = 'equipment_sessions'


class HeartRateRecord(Model):
    """
    ORM model for the heart_rate_records table.
    Represents a heart rate measurement for a member (no equipment session required).
    """
    id = AutoField()
    member_id = CharField()
    bpm = FloatField()
    measured_at = DateTimeField()
    created_at = DateTimeField()

    class Meta:
        database = db
        table_name = 'heart_rate_records'

