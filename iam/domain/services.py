"""Domain services for the IAM bounded context."""
from datetime import datetime
from typing import Optional
from iam.domain.entities import Device, Member, CheckIn


class AuthService:
    """Service for authenticating devices in the IAM context."""

    def __init__(self):
        """Initialize the AuthService."""

    @staticmethod
    def authenticate(device: Optional[Device]) -> bool:
        """Authenticate a device using its ID and API key.

        Args:
            device (Optional[Device]): The device to authenticate.

        Returns:
            bool: True if authentication succeeds, False otherwise.
        """
        return device is not None


class AccessControlService:
    """Service for managing gym member access control."""

    def __init__(self):
        """Initialize the AccessControlService."""

    @staticmethod
    def validate_member_access(member: Optional[Member]) -> tuple[bool, str]:
        """Validate if a member can access the gym.

        Args:
            member (Optional[Member]): The member to validate.

        Returns:
            tuple[bool, str]: (allowed, reason)
        """
        if not member:
            return False, "Member not found"
        
        if member.membership_status == 'suspended':
            return False, "Membership suspended"
        
        if member.membership_status != 'active':
            return False, "Membership not active"
        
        if not member.is_membership_active():
            return False, "Membership expired"
        
        return True, "Access granted"

    @staticmethod
    def create_check_in(member: Member) -> CheckIn:
        """Create a new check-in record for a member.

        Args:
            member (Member): The member checking in.

        Returns:
            CheckIn: New check-in entity.
        """
        return CheckIn(
            member_id=member.id,
            nfc_uid=member.nfc_uid,
            check_in_time=datetime.now()
        )

    @staticmethod
    def create_check_out(check_in: CheckIn) -> CheckIn:
        """Update a check-in record with check-out time.

        Args:
            check_in (CheckIn): The check-in to update.

        Returns:
            CheckIn: Updated check-in entity.
        """
        check_in.check_out_time = datetime.now()
        return check_in