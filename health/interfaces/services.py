"""Interface services for the simplified health bounded context."""
import os
from typing import Dict

import requests
from flask import Blueprint, request, jsonify

equipment_api = Blueprint("equipment_api", __name__)

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8080")
BACKEND_TOKEN = os.getenv("BACKEND_TOKEN")  # Bearer token for secured backend


def _backend_headers() -> Dict[str, str]:
    """Build headers for forwarding to backend."""
    headers = {"Content-Type": "application/json"}
    if BACKEND_TOKEN:
        headers["Authorization"] = f"Bearer {BACKEND_TOKEN}"
    return headers


@equipment_api.route("/api/check/out", methods=["POST"])
def forward_check_out():
    """Forward check-out/in request from ESP32 to backend."""
    try:
        url = f"{BACKEND_BASE_URL}/api/check/out"
        resp = requests.post(url, headers=_backend_headers(), timeout=5)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": f"Forwarding failed: {str(e)}"}), 502


@equipment_api.route("/api/heart-rate/<member_id>", methods=["POST"])
def forward_heart_rate(member_id: str):
    """Forward heart rate data from ESP32 to backend."""
    data = request.json or {}
    try:
        bpm = data["bpm"]
        url = f"{BACKEND_BASE_URL}/api/heart-rate/{member_id}"
        resp = requests.post(url, json={"bpm": bpm}, headers=_backend_headers(), timeout=5)
        return jsonify(resp.json()), resp.status_code
    except KeyError:
        return jsonify({"error": "Missing required field: bpm"}), 400
    except Exception as e:
        return jsonify({"error": f"Forwarding failed: {str(e)}"}), 502

