
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
 
#====================== GetProfile ======================
@user_bp.route('/GetProfile', methods=['GET'])
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
            "message": "User not found"
        }), 404

    access_token = generate_token(user)

    return jsonify({
        "success": True,
        "access_token": access_token,
        "data": user
    }), 200
