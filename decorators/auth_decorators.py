from functools import wraps
from utils.methods import exception_handler
from flask import g, jsonify, request
from database.db import db
from bson import ObjectId
import os
from jsonwebtoken import decode, encode
from utils.validator import Validator
from datetime import datetime, UTC
from utils.methods import generate_hash
from utils.response_messages import *
from utils.constants import UserTypes


def authorize(handler):
    @exception_handler
    @wraps(handler)
    def decorator_fun(*args, **kwargs):
        authorization = request.headers.get("authorization")

        if authorization is None or not authorization.startswith("Bearer"):
            return jsonify({
                "status": "fail",
                "message": "please login"
            }), 401

        token = authorization.split(" ")[1]

        if token is None:
            return jsonify({
                "status": "fail",
                "message": "token not found"
            }), 401
        secret = os.environ.get("JWT_SECRET_KEY")
        decoded_token = decode(token, secret, algorithms=["HS256"])

        user_id = decoded_token.get("user_id")

        user = db.get_collection("users").find_one({
            "_id": ObjectId(user_id)
        })

        if user is None:
            return jsonify({
                "status": "fail",
                "message": "user not found"
            }), 401

        g.user_data = user
        return handler(*args, **kwargs)

    return decorator_fun


def access_permission(authorized_users: list):
    @exception_handler
    def decorated_fun(handler):
        @wraps(handler)
        def decorated_fun(*args, **kwargs):
            current_user_type = g.user_data.get("user_type")
            if current_user_type not in authorized_users:
                return jsonify({
                    "status": "fail",
                    "message": "you can not access this route"
                }), 401

            return handler(*args, **kwargs)

        return decorated_fun

    return decorated_fun


def check_mobile_number(handler):
    @exception_handler
    @wraps(handler)
    def decorator_fun(*args, **kwargs):
        validator = (Validator(request.get_json())
                     .field("mobile_number")
                     .required("Please enter the mobile number")
                     .execute())

        mobile_number = validator.get("mobile_number")

        user = db.get_collection("users").find_one({
            "mobile_number": mobile_number
        },
            projection={
                "mobile_number": 1
        }
        )

        if user is not None:
            return jsonify({
                "status": "fail",
                "message": "please use different number"
            }), 400

        return handler(*args, **kwargs)

    return decorator_fun


def verify_code(handler):
    @exception_handler
    @wraps(handler)
    def decorator_fun(*args, **kwargs):
        data = request.get_json()
        validator = (Validator(data)
                     .field("mobile_number")
                     .required("Please provide the mobile number")
                     .match_pattern(r'^[0-9]{10}$', INVALID_MOBILE_NUMBER)
                     .field("code")
                     .required("please provide the verification code")
                     .validate(lambda value: len(str(value)) == 4, "Please provide a valid verification code")
                     .is_number("Verification code must be a number")
                     .field("expires_at")
                     .required("Please provide the expires at")
                     .field("hash")
                     .required("Please provide the hash")
                     .execute())

        mobile_number = validator.get("mobile_number")
        code = validator.get("code")
        expires_at = validator.get("expires_at")
        user_hash = validator.get("hash")

        print(request.get_json())

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


def verify_admin_account(handler):
    @exception_handler
    @wraps(handler)
    def decorator_fun(*args, **kwargs):
        data = (Validator(request.get_json())
                .field("mobile_number")
                .required("please provide the mobile number")
                .execute())

        admin = db.get_collection("users").find_one({
            "mobile_number": data.get("mobile_number"),
            "user_type": UserTypes.ADMIN.value
        }, projection={
            "mobile_number": 1
        })

        if admin is None:
            return jsonify({
                "status": "fail",
                "message": "admin account not found"
            })

        return handler(*args, **kwargs)
    return decorator_fun
