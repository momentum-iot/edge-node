"""
Database initialization for the PumpUp Gym Edge Service.

Sets up the SQLite database and creates required tables for devices, members, check-ins, and equipment usage.
"""
from peewee import SqliteDatabase

# Initialize SQLite database
db = SqliteDatabase('gym_edge.db')

def init_db() -> None:
    """
    Initialize the database and create tables for all models.
    """
    if not db.is_closed():
        db.close()
    db.connect()
    from iam.infrastructure.models import Device, Member, CheckIn
    from health.infrastructure.models import Equipment, EquipmentSession, HeartRateRecord
    db.create_tables([Device, Member, CheckIn, Equipment, EquipmentSession, HeartRateRecord], safe=True)
    db.close()

