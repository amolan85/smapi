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

society_bp = Blueprint('society', __name__)
 
 
 
# ====================== Add Society ======================
@society_bp.route('/AddSociety', methods=['POST'])
@jwt_required()
def AddSociety():

    current_user_id = get_jwt_identity()

    # Basic fields
    society_code = request.form.get('society_code')
    flat_unit_number = request.form.get('flat_unit_number')
    ownership_type = request.form.get('ownership_type')
    is_property_on_rent = request.form.get('is_property_on_rent')

    # Tenant specific fields
    landlord_name = request.form.get('landlord_name')
    rent_from = request.form.get('rent_from')
    rent_to = request.form.get('rent_to')

    witness1_name = request.form.get('witness1_name')
    witness1_mobile = request.form.get('witness1_mobile')
    witness2_name = request.form.get('witness2_name')
    witness2_mobile = request.form.get('witness2_mobile')

    # Files
    agreement = request.files.get('agreement')
    id_proof = request.files.get('id_proof')

    if not society_code or not flat_unit_number or not ownership_type:
        return jsonify({
            "success": False,
            "message": "Required fields missing"
        }), 400

    # If Tenant → landlord + dates mandatory
    if ownership_type == "Tenant":
        if not landlord_name or not rent_from or not rent_to:
            return jsonify({
                "success": False,
                "message": "Landlord details required for Tenant"
            }), 400

    import os, uuid

    UPLOAD_FOLDER = "uploads"
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    agreement_filename = None
    id_proof_filename = None

    if agreement:
        agreement_filename = f"{uuid.uuid4()}_{agreement.filename}"
        agreement.save(os.path.join(UPLOAD_FOLDER, agreement_filename))

    if id_proof:
        id_proof_filename = f"{uuid.uuid4()}_{id_proof.filename}"
        id_proof.save(os.path.join(UPLOAD_FOLDER, id_proof_filename))

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO user_societies
        (user_id, society_code, flat_unit_number, ownership_type,
         is_property_on_rent, landlord_name, rent_from, rent_to,
         agreement_file, id_proof_file,
         witness1_name, witness1_mobile,
         witness2_name, witness2_mobile)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        int(current_user_id),
        society_code,
        flat_unit_number,
        ownership_type,
        is_property_on_rent == "true",
        landlord_name,
        rent_from,
        rent_to,
        agreement_filename,
        id_proof_filename,
        witness1_name,
        witness1_mobile,
        witness2_name,
        witness2_mobile
    ))

    db.commit()

    return jsonify({
        "success": True,
        "status code":200,
        "message": "Society added successfully"
    }), 200
