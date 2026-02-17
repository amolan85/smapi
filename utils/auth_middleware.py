from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from database.db import get_db_connection
from utils.password_utils import hash_password, check_password
import uuid
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)
