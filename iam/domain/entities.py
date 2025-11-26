"""Domain entities for the IAM bounded context."""
from datetime import datetime
from typing import Optional


class Device:
    """Represents an IoT device entity (ESP32) in the IAM context.

    Attributes:
        device_id (str): Unique identifier for the device.
        api_key (str): API key for device authentication.
        created_at (datetime): Timestamp when the device was created.
    """

    def __init__(self, device_id: str, api_key: str, created_at):
        """Initialize a Device instance.

        Args:
            device_id (str): Unique identifier for the device.
            api_key (str): API key for authentication.
            created_at (datetime): Creation timestamp.
        """
        self.device_id = device_id
        self.api_key = api_key
        self.created_at = created_at


class Member:
    """Represents a gym member entity.

    Attributes:
        id (int): Unique identifier for the member.
        nfc_uid (str): NFC card UID for access control.
        name (str): Full name of the member.
        email (str): Email address.
        membership_status (str): Status of membership (active, expired, suspended).
        membership_expiry (datetime): Expiration date of membership.
        created_at (datetime): Timestamp when the member was registered.
    """

    def __init__(self, nfc_uid: str, name: str, email: str, 
                 membership_status: str, membership_expiry: datetime,
                 created_at: datetime, id: Optional[int] = None):
        """Initialize a Member instance.

        Args:
            nfc_uid (str): NFC card UID.
            name (str): Full name.
            email (str): Email address.
            membership_status (str): Membership status.
            membership_expiry (datetime): Membership expiration date.
            created_at (datetime): Registration timestamp.
            id (int, optional): Member ID.
        """
        self.id = id
        self.nfc_uid = nfc_uid
        self.name = name
        self.email = email
        self.membership_status = membership_status
        self.membership_expiry = membership_expiry
        self.created_at = created_at

    def is_membership_active(self) -> bool:
        """Check if the member has an active membership.

        Returns:
            bool: True if membership is active and not expired.
        """
        if self.membership_status != 'active':
            return False
        return datetime.now() < self.membership_expiry


class CheckIn:
    """Represents a check-in/check-out record.

    Attributes:
        id (int): Unique identifier for the check-in record.
        member_id (int): ID of the member.
        nfc_uid (str): NFC UID used for check-in.
        check_in_time (datetime): Timestamp of check-in.
        check_out_time (datetime): Timestamp of check-out (None if still inside).
        created_at (datetime): Record creation timestamp.
    """

    def __init__(self, member_id: int, nfc_uid: str, check_in_time: datetime,
                 check_out_time: Optional[datetime] = None,
                 created_at: Optional[datetime] = None, id: Optional[int] = None):
        """Initialize a CheckIn instance.

        Args:
            member_id (int): Member ID.
            nfc_uid (str): NFC UID.
            check_in_time (datetime): Check-in timestamp.
            check_out_time (datetime, optional): Check-out timestamp.
            created_at (datetime, optional): Record creation timestamp.
            id (int, optional): Check-in record ID.
        """
        self.id = id
        self.member_id = member_id
        self.nfc_uid = nfc_uid
        self.check_in_time = check_in_time
        self.check_out_time = check_out_time
        self.created_at = created_at or datetime.now()

    def is_active(self) -> bool:
        """Check if this is an active check-in (no check-out yet).

        Returns:
            bool: True if member hasn't checked out yet.
        """
        return self.check_out_time is None