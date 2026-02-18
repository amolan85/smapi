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

auth_bp = Blueprint('auth', __name__)
 
# # ================= LOGIN API =================
# @auth_bp.route('/login', methods=['POST'])
# def login():

#     data = request.get_json()

#     if not data or not data.get("email") or not data.get("password"):
#         return jsonify({"message": "Email and password required"}), 400

#     email = data.get("email")
#     password = data.get("password")

#     db = get_db_connection()
#     cursor = db.cursor(dictionary=True)

#     cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
#     user = cursor.fetchone()

#     if not user:
#         return jsonify({"message": "User not found"}), 404

#     if not check_password(password, user["password"]):
#         return jsonify({"message": "Invalid password"}), 401

#     access_token = create_access_token(
#         identity=user["id"],
#         additional_claims={"role": user["role"]}
#     )

#     return jsonify({
#         "message": "Login successful",
#         "access_token": access_token,
#         "role": user["role"]
#     }), 200
@auth_bp.route('/send-otp', methods=['POST'])
def send_otp():

    data = request.get_json()

    if not data or not data.get("mobile"):
        return jsonify({"message": "Mobile number required"}), 400

    mobile = data.get("mobile")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE mobile = %s", (mobile,))
    user = cursor.fetchone()

    if not user:
        return   jsonify({
    "success": False,
    "status_code": 404,
    "message": "Invalid Mobile No.",
    "data": {
         
           }
     }),404

    otp = "123456"

    cursor.execute("""
        UPDATE users
        SET otp = %s,
            otp_expiry = DATE_ADD(NOW(), INTERVAL 5 MINUTE)
        WHERE mobile = %s
    """, (otp, mobile))

    db.commit()
 
    access_token = generate_token(user)

    return jsonify({
    "success": True,
    "status_code": 200,
    "message": "OTP sent successfully",
    "data": {
        "mobile": mobile,
        "access_token": access_token,
        "otp":otp
           }
     }), 200

 
# ================= VERIFY OTP =================
@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():

    data = request.get_json()

    if not data or not data.get("mobile") or not data.get("otp"):
        return jsonify({"message": "Mobile and OTP required"}), 400

    mobile = data.get("mobile")
    otp = data.get("otp")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM users
        WHERE mobile = %s
        AND otp = %s
        AND otp_expiry > NOW()
    """, (mobile, otp))

    user = cursor.fetchone()

    if not user:
        return jsonify({"message": "Invalid or expired OTP"}), 401

    # Clear OTP after verification
    cursor.execute("""
        UPDATE users
        SET otp = NULL,
            otp_expiry = NULL
        WHERE id = %s
    """, (user["id"],))

    db.commit()

    access_token = create_access_token(
        identity=user["id"],
        additional_claims={"role": user["role"]}
    )

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "role": user["role"]
    }), 200
 
# ================= FORGOT PASSWORD =================
@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():

    data = request.get_json()

    if not data or not data.get("email"):
        return jsonify({"message": "Email required"}), 400

    email = data.get("email")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if not user:
        return jsonify({"message": "User not found"}), 404

    reset_token = str(uuid.uuid4())
    expiry_time = datetime.now() + timedelta(minutes=15)

    cursor.execute("""
        UPDATE users
        SET reset_token = %s,
            reset_token_expiry = %s
        WHERE email = %s
    """, (reset_token, expiry_time, email))

    db.commit()

    return jsonify({
        "message": "Reset token generated",
        "reset_token": reset_token
    }), 200


# ================= RESET PASSWORD =================
@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():

    data = request.get_json()

    if not data or not data.get("token") or not data.get("new_password"):
        return jsonify({"message": "Token and new password required"}), 400

    token = data.get("token")
    new_password = data.get("new_password")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM users
        WHERE reset_token = %s
        AND reset_token_expiry > NOW()
    """, (token,))

    user = cursor.fetchone()

    if not user:
        return jsonify({"message": "Invalid or expired token"}), 400

    hashed = hash_password(new_password).decode('utf-8')

    cursor.execute("""
        UPDATE users
        SET password = %s,
            reset_token = NULL,
            reset_token_expiry = NULL
        WHERE id = %s
    """, (hashed, user["id"]))

    db.commit()

    return jsonify({"message": "Password reset successful"}), 200
