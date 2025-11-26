"""Repositories for the IAM bounded context."""
from datetime import datetime
from typing import Optional, List

import peewee

from iam.domain.entities import Device, Member, CheckIn
from iam.infrastructure.models import Device as DeviceModel, Member as MemberModel, CheckIn as CheckInModel


class DeviceRepository:
    """Repository for managing Device entities."""

    @staticmethod
    def find_by_id_and_api_key(device_id: str, api_key: str) -> Optional[Device]:
        """Find a device by its ID and API key.

        Args:
            device_id (str): Unique identifier of the device.
            api_key (str): API key for authentication.

        Returns:
            Optional[Device]: Device entity if found, None otherwise.
        """
        try:
            device = DeviceModel.get(
                (DeviceModel.device_id == device_id) & (DeviceModel.api_key == api_key)
            )
            return Device(device.device_id, device.api_key, device.created_at)
        except peewee.DoesNotExist:
            return None

    @staticmethod
    def get_or_create_test_device() -> Device:
        """Get or create a test device for development.

        Returns:
            Device: The test device entity.
        """
        device, _ = DeviceModel.get_or_create(
            device_id="gym-esp32-001",
            defaults={"api_key": "gym-api-key-2025", "created_at": datetime.now()}
        )
        return Device(device.device_id, device.api_key, device.created_at)


class MemberRepository:
    """Repository for managing Member entities."""

    @staticmethod
    def find_by_nfc_uid(nfc_uid: str) -> Optional[Member]:
        """Find a member by NFC UID.

        Args:
            nfc_uid (str): NFC card UID.

        Returns:
            Optional[Member]: Member entity if found, None otherwise.
        """
        try:
            member = MemberModel.get(MemberModel.nfc_uid == nfc_uid)
            return Member(
                nfc_uid=member.nfc_uid,
                name=member.name,
                email=member.email,
                membership_status=member.membership_status,
                membership_expiry=member.membership_expiry,
                created_at=member.created_at,
                id=member.id
            )
        except peewee.DoesNotExist:
            return None

    @staticmethod
    def save(member: Member) -> Member:
        """Save a member to the database.

        Args:
            member (Member): Member entity to save.

        Returns:
            Member: Saved member with ID.
        """
        if member.id:
            # Update existing
            MemberModel.update(
                nfc_uid=member.nfc_uid,
                name=member.name,
                email=member.email,
                membership_status=member.membership_status,
                membership_expiry=member.membership_expiry
            ).where(MemberModel.id == member.id).execute()
            return member
        else:
            # Create new
            member_model = MemberModel.create(
                nfc_uid=member.nfc_uid,
                name=member.name,
                email=member.email,
                membership_status=member.membership_status,
                membership_expiry=member.membership_expiry,
                created_at=member.created_at
            )
            member.id = member_model.id
            return member

    @staticmethod
    def get_or_create_test_member() -> Member:
        """Get or create a test member for development.

        Returns:
            Member: Test member entity.
        """
        from datetime import timedelta
        expiry = datetime.now() + timedelta(days=30)
        
        member_model, _ = MemberModel.get_or_create(
            nfc_uid="04A1B2C3D4E5F6",  # Example NFC UID
            defaults={
                "name": "John Doe",
                "email": "john.doe@example.com",
                "membership_status": "active",
                "membership_expiry": expiry,
                "created_at": datetime.now()
            }
        )
        return Member(
            nfc_uid=member_model.nfc_uid,
            name=member_model.name,
            email=member_model.email,
            membership_status=member_model.membership_status,
            membership_expiry=member_model.membership_expiry,
            created_at=member_model.created_at,
            id=member_model.id
        )


class CheckInRepository:
    """Repository for managing CheckIn entities."""

    @staticmethod
    def save(check_in: CheckIn) -> CheckIn:
        """Save a check-in record to the database.

        Args:
            check_in (CheckIn): CheckIn entity to save.

        Returns:
            CheckIn: Saved check-in with ID.
        """
        if check_in.id:
            # Update existing (for check-out)
            CheckInModel.update(
                check_out_time=check_in.check_out_time
            ).where(CheckInModel.id == check_in.id).execute()
            return check_in
        else:
            # Create new check-in
            check_in_model = CheckInModel.create(
                member=check_in.member_id,
                nfc_uid=check_in.nfc_uid,
                check_in_time=check_in.check_in_time,
                check_out_time=check_in.check_out_time,
                created_at=check_in.created_at
            )
            check_in.id = check_in_model.id
            return check_in

    @staticmethod
    def find_active_by_member_id(member_id: int) -> Optional[CheckIn]:
        """Find an active check-in (no check-out) for a member.

        Args:
            member_id (int): Member ID.

        Returns:
            Optional[CheckIn]: Active check-in if found, None otherwise.
        """
        try:
            check_in = CheckInModel.get(
                (CheckInModel.member == member_id) & 
                (CheckInModel.check_out_time.is_null())
            )
            return CheckIn(
                member_id=check_in.member.id,
                nfc_uid=check_in.nfc_uid,
                check_in_time=check_in.check_in_time,
                check_out_time=check_in.check_out_time,
                created_at=check_in.created_at,
                id=check_in.id
            )
        except peewee.DoesNotExist:
            return None

    @staticmethod
    def count_active_check_ins() -> int:
        """Count the number of active check-ins (members currently in the gym).

        Returns:
            int: Number of active check-ins.
        """
        return CheckInModel.select().where(CheckInModel.check_out_time.is_null()).count()

    @staticmethod
    def get_all_active() -> List[CheckIn]:
        """Get all active check-ins.

        Returns:
            List[CheckIn]: List of active check-in entities.
        """
        check_ins = CheckInModel.select().where(CheckInModel.check_out_time.is_null())
        return [
            CheckIn(
                member_id=c.member.id,
                nfc_uid=c.nfc_uid,
                check_in_time=c.check_in_time,
                check_out_time=c.check_out_time,
                created_at=c.created_at,
                id=c.id
            )
            for c in check_ins
        ]