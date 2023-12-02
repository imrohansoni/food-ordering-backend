import os
import json

from database.db import db
from flask import request, jsonify, g
from datetime import datetime, UTC, timedelta
from random import randint
from hashlib import sha256
from jsonwebtoken import encode, decode
from functools import wraps
from bson import ObjectId
from utils.validator import Validator
from utils.methods import exception_handler
from utils.constants import UserTypes


def generate_hash(data):
    json_data = json.dumps({
        **data
    }, sort_keys=True) + os.environ.get("HASH_SECRET")

    hash_string = sha256(json_data.encode()).hexdigest()
    return hash_string


@exception_handler
def verify_code(handler):
    @wraps(handler)
    def decorator_fun(*args, **kwargs):
        data = request.get_json()
        validator = (Validator(data)
                     .field("mobile_number")
                     .required("Please provide the mobile number")
                     .field("code")
                     .required("please provide the verification code")
                     .field("expires_at")
                     .required("Please provide the expires at")
                     .field("hash")
                     .required("Please provide the hash")
                     .execute())

        mobile_number = validator.get("mobile_number")
        code = validator.get("code")
        expires_at = validator.get("expires_at")
        user_hash = validator.get("hash")

        if datetime.now(UTC) > datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S.%f%z"):
            return jsonify({
                "status": "fail",
                "message": "verification code is expired"
            }), 400

        hash_string = generate_hash({
            "mobile_number": mobile_number,
            "code": code,
            "expires_at": expires_at,
        })

        if hash_string != user_hash:
            return jsonify({
                "status": "fail",
                "message": "wrong verification code, please try again"
            }), 400

        return handler(*args, **kwargs)
    return decorator_fun


@exception_handler
def login():
    data = request.get_json()
    user = db["users"].find_one({
        "mobile_number": data.get("mobile_number")
    })

    user_id = None

    if user is None:
        result = db["users"].insert_one({
            "mobile_number": data.get("mobile_number"),
            "created_at": datetime.now(UTC),
            "user_type": UserTypes.CUSTOMER.value,
            "last_updated_at": datetime.now(UTC)
        })
        user_id = result.inserted_id
    else:
        user_id = user.get("_id")

    auth_token = encode({
        "user_id": str(user_id)
    }, os.getenv("JWT_SECRET_KEY"))

    return jsonify({
        "status": "success",
        "data": {
            "auth_token": auth_token
        }
    })


@exception_handler
def send_code():
    validator = (Validator(request.get_json())
                 .field("mobile_number")
                 .required("Please provide the mobile number")
                 .execute())

    mobile_number = validator.get("mobile_number")

    code = randint(1234, 9876)
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
def check_mobile_number(handler):
    @wraps(handler)
    def decorator_fun(*args, **kwargs):
        validator = (Validator(request.get_json())
                     .field("mobile_number")
                     .required("Please enter the mobile number")
                     .execute())

        mobile_number = validator.get("mobile_number")

        user = db.get_collection("users").find_one({
            "mobile_number": mobile_number
        }, {
            "$projection": {
                "mobile_number": 1
            }
        })

        if user is not None:
            return jsonify({
                "status": "fail",
                "message": "please use different number"
            })

        return handler(*args, **kwargs)
    return decorator_fun


@exception_handler
def update_mobile():
    mobile_number = request.get_json()
    user_id = g.user_data.get("_id")

    result = db.get_collection("users").update_one({
        "_id": ObjectId(user_id),
        "active": True
    }, {
        "$set": {
            "mobile_number": mobile_number
        }
    })

    if result.matched_count < 1:
        return jsonify({
            "status": "fail",
            "message": "user not found"
        }), 404

    return jsonify({
        "status": "success",
        "message": "your number is updated"
    })
