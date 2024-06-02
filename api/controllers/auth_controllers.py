import os
import random
from datetime import datetime, timezone, timedelta
from random import randint

from bson import ObjectId
from flask import request, jsonify, g
import requests
from jsonwebtoken import encode, decode
from bcrypt import checkpw, gensalt, hashpw
from database.db import get_db
from utils.validator import Validator
from utils.methods import exception_handler, generate_hash
from utils.constants import UserTypes, Environment
from utils.response_messages import INVALID_MOBILE_NUMBER, NO_MOBILE


@exception_handler
def login():
    data = request.get_json()
    db = get_db()

    user = db["users"].find_one({
        "mobile_number": data.get("mobile_number")
    })
    utc_now = datetime.now(timezone.utc)

    if user is None:
        result = db["users"].insert_one({
            "mobile_number": data.get("mobile_number"),
            "created_at": utc_now,
            "user_type": UserTypes.CUSTOMER.value,
            "active": True,
            "last_updated_at": utc_now
        })
        user_id = result.inserted_id
    else:
        user_id = user.get("_id")

    auth_token = encode({
        "user_id": str(user_id),
        "exp": utc_now + timedelta(days=90)
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

    code = randint(1234, 4321)

    send_sms = os.environ.get("SEND_SMS") == "true"
    flask_env = os.environ.get("FLASK_ENV")

    if flask_env == Environment.PRODUCTION.value and send_sms:
        sms_response = requests.get(os.environ.get("SMS_BASE_URL"), params={
            "route": "otp",
            "authorization": os.environ.get("SMS_AUTHORIZATION"),
            "variables_values": code,
            "flash": 0,
            "numbers": mobile_number
        }, timeout=2000)
        response = sms_response.json()

        if response.get("return") is False:
            print(code)
            return jsonify({
                "status": "fail",
                "message": response.get("message")
            })
    else:
        print(f"verification code = {code}")

    utc_now = datetime.now(timezone.utc)

    expires_at = str(
        utc_now + timedelta(minutes=int(os.environ.get("VERIFICATION_CODE_EXPIRES"))))

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
    db = get_db()
    data = (Validator(request.get_json())
            .field("mobile_number")
            .required("please provide the mobile number")
            .field("password")
            .required("please provide the password")
            .execute())

    admin = db["users"].find_one({
        "mobile_number": data.get("mobile_number"),
        "user_type": "admin"
    }, projection={
        "mobile_number": 1,
        "password_updated_at": 1,
        "password": 1
    })

    if admin is None:
        return jsonify({
            "ok": False,
            "status": "fail",
            "errors": {
                'mobile_number': "mobile number doesn't exit"
            }
        })

    user_password = data.get("password").encode("utf-8")
    hashed_password = admin["password"].encode("utf-8")

    password_matched = checkpw(user_password, hashed_password)

    if not password_matched:
        return jsonify({
            "ok": False,
            "status": "fail",
            "errors": {
                'password': 'password is incorrect'
            }
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
    db = get_db()
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

    result = db["users"].update_one({
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


@exception_handler
def send_password_reset_token():
    db = get_db()
    user = request.get_json()
    mobile_number = user.get("mobile_number")

    user = db["users"].find_one({
        "mobile_number": mobile_number,
        "user_type": UserTypes.ADMIN.value
    }, projection={
        "_id": 1
    })
    utc_now = datetime.now(timezone.utc)

    password_reset_token = encode(
        payload={
            "user_id": str(user["_id"]),
            "exp": utc_now + timedelta(minutes=5)
        },
        key=os.environ.get("JWT_SECRET_KEY"))

    return jsonify({
        "status": "success",
        "data": {
            "password_reset_token": password_reset_token
        }
    })


@exception_handler
def reset_password():
    db = get_db()

    data = (Validator(request.get_json())
            .field("password_reset_token")
            .required("please provide the password reset token")
            .field("new_password")
            .required("please enter the new password")
            .execute())

    decoded_token = decode(data.get("password_reset_token"),
                           key=os.environ.get("JWT_SECRET_KEY"),
                           algorithms=["HS256"])

    user_id = decoded_token.get("user_id")

    new_hashed_password = data.get("new_password").encode('utf-8')

    db["users"].update_one({
        "_id": ObjectId(user_id)
    }, {
        "$set": {
            "password": hashpw(new_hashed_password, gensalt()).decode('utf-8')
        }
    })

    return jsonify({
        "status": "success",
        "message": "password is updated"
    })
