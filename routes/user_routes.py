
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from database.db import get_db_connection
from utils.password_utils import hash_password, check_password
from utils.Tokens_utils import generate_token

import uuid
from datetime import datetime, timedelta

user_bp = Blueprint('user', __name__)
 
 
# ====================== GetProfile ======================
@user_bp.route('/GetProfile', methods=['POST'])
@jwt_required()
def GetProfile():

    current_user_id = get_jwt_identity()

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, first_name, last_name, email, mobile, role
        FROM users
        WHERE id = %s
    """, (int(current_user_id),))

    user = cursor.fetchone()

    if not user:
        return jsonify({
            "success": False,
            "status code": 404,
            "message": "User not found"
        }), 404

    return jsonify({
        "success": True,
        "status code": 200,
        "data": user
    }), 200


  #============================UpdateProfile=================================================== 
@user_bp.route('/UpdateProfile', methods=['POST'])
@jwt_required()
def UpdateProfile():

    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400

    fields = []
    values = []

    allowed_fields = ["first_name", "last_name", "email"]

    for key in allowed_fields:
        if key in data:
            fields.append(f"{key} = %s")
            values.append(data[key])

    if not fields:
        return   jsonify({
        "success": False,
        "status code": 400,
        "message": "user not found"
    }), 400

    values.append(int(current_user_id))

    db = get_db_connection()
    cursor = db.cursor()

    query = f"UPDATE users SET {', '.join(fields)} WHERE id = %s"
    cursor.execute(query, tuple(values))
    db.commit()

    return jsonify({
        "success": True,
        "status code": 200,
        "message": "Profile updated successfully"
    }), 200
