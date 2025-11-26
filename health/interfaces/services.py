"""Interface services for the Equipment Usage bounded context."""
from flask import Blueprint, request, jsonify

from health.application.services import EquipmentSessionApplicationService, HeartRateApplicationService
from iam.interfaces.services import authenticate_request

equipment_api = Blueprint("equipment_api", __name__)

# Initialize dependencies
session_service = EquipmentSessionApplicationService()
hr_service = HeartRateApplicationService()


@equipment_api.route("/api/v1/equipment/session/start", methods=["POST"])
def start_equipment_session():
    """Handle POST request to start an equipment usage session.

    Expects JSON with device_id, member_id, and equipment_id.

    Returns:
        tuple: (JSON response, status code).
    """
    auth_result = authenticate_request()
    if auth_result:
        return auth_result

    data = request.json
    try:
        member_id = data["member_id"]
        equipment_id = data["equipment_id"]
        
        result = session_service.start_equipment_session(member_id, equipment_id)
        
        if result["success"]:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
    except KeyError as e:
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500


@equipment_api.route("/api/v1/equipment/session/end", methods=["POST"])
def end_equipment_session():
    """Handle POST request to end an equipment usage session.

    Expects JSON with device_id and member_id.

    Returns:
        tuple: (JSON response, status code).
    """
    auth_result = authenticate_request()
    if auth_result:
        return auth_result

    data = request.json
    try:
        member_id = data["member_id"]
        
        result = session_service.end_equipment_session(member_id)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
    except KeyError as e:
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500


@equipment_api.route("/api/v1/equipment/heart-rate", methods=["POST"])
def record_heart_rate():
    """Handle POST request to record heart rate data.

    Expects JSON with device_id, session_id, member_id, and bpm.

    Returns:
        tuple: (JSON response, status code).
    """
    auth_result = authenticate_request()
    if auth_result:
        return auth_result

    data = request.json
    try:
        session_id = data["session_id"]
        member_id = data["member_id"]
        bpm = data["bpm"]
        
        result = hr_service.record_heart_rate(session_id, member_id, bpm)
        
        if result["success"]:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
    except KeyError as e:
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500




