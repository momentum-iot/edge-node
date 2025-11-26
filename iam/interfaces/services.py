"""Interface services for the IAM bounded context."""
from flask import Blueprint, request, jsonify
from iam.application.services import AuthApplicationService, AccessControlApplicationService

iam_api = Blueprint("iam_api", __name__)

# Initialize dependencies
auth_service = AuthApplicationService()
access_control_service = AccessControlApplicationService()


def authenticate_request():
    """Authenticate an incoming HTTP request.

    Checks for device_id in the JSON body and X-API-Key in headers.

    Returns:
        tuple: (JSON response, status code) if authentication fails, None if successful.
    """
    device_id = request.json.get("device_id") if request.json else None
    api_key = request.headers.get("X-API-Key")
    if not device_id or not api_key:
        return jsonify({"error": "Missing device_id or X-API-Key"}), 401
    if not auth_service.authenticate(device_id, api_key):
        return jsonify({"error": "Invalid device_id or API key"}), 401
    return None


@iam_api.route("/api/v1/access/nfc-scan", methods=["POST"])
def process_nfc_scan():
    """Handle NFC card scan for check-in/check-out.

    Expects JSON with device_id and nfc_uid.
    Automatically handles check-in or check-out based on member's current status.

    Returns:
        tuple: (JSON response, status code).
    """
    auth_result = authenticate_request()
    if auth_result:
        return auth_result

    data = request.json
    try:
        nfc_uid = data["nfc_uid"]
        result = access_control_service.process_nfc_access(nfc_uid)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 403
    except KeyError:
        return jsonify({"error": "Missing required field: nfc_uid"}), 400
    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500


@iam_api.route("/api/v1/access/occupancy", methods=["GET"])
def get_occupancy():
    """Get current gym occupancy.

    Returns:
        tuple: (JSON response with current occupancy count, status code).
    """
    # Simple GET request - no body, so check headers only
    api_key = request.headers.get("X-API-Key")
    device_id = request.args.get("device_id")  # Optional query param
    
    if not api_key:
        return jsonify({"error": "Missing X-API-Key header"}), 401
    
    if device_id and not auth_service.authenticate(device_id, api_key):
        return jsonify({"error": "Invalid device_id or API key"}), 401

    try:
        count = access_control_service.get_current_occupancy()
        return jsonify({
            "current_occupancy": count,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500