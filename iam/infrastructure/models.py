"""Peewee models for the IAM bounded context."""
from peewee import Model, CharField, DateTimeField, AutoField, IntegerField, ForeignKeyField
from shared.infrastructure.database import db


class Device(Model):
    """Peewee model for the 'devices' table.

    Attributes:
        device_id (CharField): Unique identifier (primary key).
        api_key (CharField): API key for authentication.
        created_at (DateTimeField): Creation timestamp.
    """
    device_id   = CharField(primary_key=True)
    api_key     = CharField()
    created_at  = DateTimeField()

    class Meta:
        """Metadata for the Device model."""
        database    = db
        table_name  = 'devices'


class Member(Model):
    """Peewee model for the 'members' table.

    Attributes:
        id (AutoField): Primary key.
        nfc_uid (CharField): NFC card UID (unique).
        name (CharField): Member's full name.
        email (CharField): Email address.
        membership_status (CharField): Status (active, expired, suspended).
        membership_expiry (DateTimeField): Membership expiration date.
        created_at (DateTimeField): Registration timestamp.
    """
    id = AutoField()
    nfc_uid = CharField(unique=True, index=True)
    name = CharField()
    email = CharField()
    membership_status = CharField(default='active')  # active, expired, suspended
    membership_expiry = DateTimeField()
    created_at = DateTimeField()

    class Meta:
        """Metadata for the Member model."""
        database = db
        table_name = 'members'


class CheckIn(Model):
    """Peewee model for the 'check_ins' table.

    Attributes:
        id (AutoField): Primary key.
        member_id (ForeignKeyField): Reference to Member.
        nfc_uid (CharField): NFC UID used.
        check_in_time (DateTimeField): Check-in timestamp.
        check_out_time (DateTimeField): Check-out timestamp (nullable).
        created_at (DateTimeField): Record creation timestamp.
    """
    id = AutoField()
    member = ForeignKeyField(Member, backref='check_ins', column_name='member_id')
    nfc_uid = CharField()
    check_in_time = DateTimeField()
    check_out_time = DateTimeField(null=True)
    created_at = DateTimeField()

    class Meta:
        """Metadata for the CheckIn model."""
        database = db
        table_name = 'check_ins'
