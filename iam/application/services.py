"""Application services for the IAM bounded context."""
from typing import Optional, Dict
from datetime import datetime

from iam.domain.entities import Device, Member, CheckIn
from iam.domain.services import AuthService, AccessControlService
from iam.infrastructure.repositories import DeviceRepository, MemberRepository, CheckInRepository


class AuthApplicationService:
    """Application service for device authentication."""

    def __init__(self):
        """Initialize the AuthApplicationService."""
        self.device_repository = DeviceRepository()
        self.auth_service = AuthService()

    def authenticate(self, device_id: str, api_key: str) -> bool:
        """Authenticate a device.

        Args:
            device_id (str): Unique identifier of the device.
            api_key (str): API key for authentication.

        Returns:
            bool: True if authentication succeeds, False otherwise.
        """
        device: Optional[Device] = self.device_repository.find_by_id_and_api_key(device_id, api_key)
        return self.auth_service.authenticate(device)

    def get_or_create_test_device(self) -> Device:
        """Get or create a test device for development.

        Returns:
            Device: The test device entity.
        """
        return self.device_repository.get_or_create_test_device()


class AccessControlApplicationService:
    """Application service for member access control (check-in/check-out)."""

    def __init__(self):
        """Initialize the AccessControlApplicationService."""
        self.member_repository = MemberRepository()
        self.check_in_repository = CheckInRepository()
        self.access_control_service = AccessControlService()

    def process_nfc_access(self, nfc_uid: str) -> Dict:
        """Process NFC card access (check-in or check-out).

        Args:
            nfc_uid (str): NFC card UID.

        Returns:
            Dict: Response with action taken and details.
        """
        # Find member by NFC UID
        member = self.member_repository.find_by_nfc_uid(nfc_uid)
        
        if not member:
            return {
                "success": False,
                "action": "denied",
                "reason": "Member not found",
                "nfc_uid": nfc_uid
            }

        # Validate membership
        allowed, reason = self.access_control_service.validate_member_access(member)
        
        if not allowed:
            return {
                "success": False,
                "action": "denied",
                "reason": reason,
                "member_id": member.id,
                "member_name": member.name
            }

        # Check if member has an active check-in
        active_check_in = self.check_in_repository.find_active_by_member_id(member.id)

        if active_check_in:
            # Member is checking out
            updated_check_in = self.access_control_service.create_check_out(active_check_in)
            saved_check_in = self.check_in_repository.save(updated_check_in)
            
            return {
                "success": True,
                "action": "check_out",
                "member_id": member.id,
                "member_name": member.name,
                "check_in_id": saved_check_in.id,
                "check_in_time": saved_check_in.check_in_time.isoformat(),
                "check_out_time": saved_check_in.check_out_time.isoformat(),
                "current_occupancy": self.check_in_repository.count_active_check_ins()
            }
        else:
            # Member is checking in
            new_check_in = self.access_control_service.create_check_in(member)
            saved_check_in = self.check_in_repository.save(new_check_in)
            
            return {
                "success": True,
                "action": "check_in",
                "member_id": member.id,
                "member_name": member.name,
                "check_in_id": saved_check_in.id,
                "check_in_time": saved_check_in.check_in_time.isoformat(),
                "current_occupancy": self.check_in_repository.count_active_check_ins()
            }

    def get_current_occupancy(self) -> int:
        """Get the current gym occupancy.

        Returns:
            int: Number of members currently in the gym.
        """
        return self.check_in_repository.count_active_check_ins()

    def get_or_create_test_member(self) -> Member:
        """Get or create a test member for development.

        Returns:
            Member: Test member entity.
        """
        return self.member_repository.get_or_create_test_member()