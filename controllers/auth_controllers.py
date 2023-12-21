import os
from bson import ObjectId
import requests
from database.db import db
from flask import request, jsonify, g
from datetime import datetime, UTC, timedelta
from random import randint
from jsonwebtoken import encode
from utils.validator import Validator
from utils.methods import exception_handler, generate_hash
from utils.constants import UserTypes
from utils.response_messages import *
from bcrypt import checkpw, gensalt, hashpw


@exception_handler
def login():
    data = request.get_json()
    user = db["users"].find_one({
        "mobile_number": data.get("mobile_number")
    })

    if user is None:
        result = db["users"].insert_one({
            "mobile_number": data.get("mobile_number"),
            "created_at": datetime.now(UTC),
            "user_type": UserTypes.CUSTOMER.value,
            "active": True,
            "last_updated_at": datetime.now(UTC)
        })
        user_id = result.inserted_id
    else:
        user_id = user.get("_id")

    auth_token = encode({
        "user_id": str(user_id)
    }, os.environ.get("JWT_SECRET_KEY"))

    return jsonify({
        "status": "success",
        "data": {
            "auth_token": auth_token
        }
    }), 200


@exception_handler
def send_code():
    validator = (Validator(request.get_json())
                 .field("mobile_number")
                 .required(NO_MOBILE)
                 .match_pattern(r'^[0-9]{10}$', INVALID_MOBILE_NUMBER)
                 .execute())

    mobile_number = validator.get("mobile_number")

    code = randint(1234, 9876)

    if os.environ.get("FLASK_ENV") == "production":
        sms_response = requests.get(os.environ.get("SMS_BASE_URL"), params={
            "route": "otp",
            "authorization": os.environ.get("SMS_AUTHORIZATION"),
            "variables_values": code,
            "flash": 0,
            "numbers": mobile_number
        })
        response = sms_response.json()

        if response.get("return") is False:
            print(response.get("message"))
    else:
        print(f"verification code = {code}")

    current_time = datetime.now(UTC)

    expires_at = str(
        current_time + timedelta(minutes=int(os.environ.get("VERIFICATION_CODE_EXPIRES"))))

    hash_string = generate_hash({
        "mobile_number": mobile_number,
        "code": code,
        "expires_at": expires_at,
    })

    return jsonify({
        "status": "success",
        "data": {
            "mobile_number": mobile_number,
            "hash": hash_string,
            "expires_at": expires_at
        }
    })


@exception_handler
def login_admin():
    data = (Validator(request.get_json())
            .field("mobile_number")
            .required("please provide the mobile number")
            .field("password")
            .required("please provide the password")
            .execute())

    admin = db.get_collection("users").find_one({
        "mobile_number": data.get("mobile_number"),
        "user_type": "admin"
    }, projection={
        "mobile_number": 1,
        "password_updated_at": 1,
        "password": 1
    })

    if admin is None:
        return jsonify({
            "status": "fail",
            "message": "account not found"
        })

    user_password = data.get("password").encode("utf-8")
    hashed_password = admin["password"].encode("utf-8")

    password_matched = checkpw(user_password, hashed_password)

    if not password_matched:
        return jsonify({
            "status": "fail",
            "message": "password is incorrect, try again"
        })

    auth_token = encode({
        "user_id": str(admin["_id"])
    }, os.environ.get("JWT_SECRET_KEY"))

    return jsonify({
        "status": "success",
        "data": {
            "auth_token": auth_token
        }
    }), 200


@exception_handler
def change_password():
    data = (Validator(request.get_json())
            .field("old_password")
            .required("please provide the old password")
            .field("new_password")
            .required("please provide the new password")
            .execute())

    current_user_id = g.user_data.get("_id")

    user_password = data.get("old_password").encode("utf-8")
    hashed_password = g.user_data.get("password").encode("utf-8")

    password_matched = checkpw(user_password, hashed_password)

    if not password_matched:
        return jsonify({
            "status": "fail",
            "message": "password is incorrect, try again"
        })

    new_hashed_password = data.get("new_password").encode('utf-8')

    result = db.get_collection("users").update_one({
        "_id": ObjectId(current_user_id)
    }, {
        "$set": {
            "password": hashpw(new_hashed_password, gensalt()).decode('utf-8')
        }
    })

    if result.modified_count < 1:
        return jsonify({
            "status": "fail",
            "message": "failed to update the password"
        })

    return jsonify({
        "status": "success",
        "message": "password is updated"
    })
