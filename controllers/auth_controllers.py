import os

import requests

from database.db import db
from flask import request, jsonify, g, current_app
from datetime import datetime, UTC, timedelta
from random import randint
from jsonwebtoken import encode
from bson import ObjectId
from utils.validator import Validator
from utils.methods import exception_handler, generate_hash
from utils.constants import UserTypes
from utils.response_messages import *


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
            "last_updated_at": datetime.now(UTC)
        })
        user_id = result.inserted_id
    else:
        user_id = user.get("_id")

    auth_token = encode({
        "user_id": str(user_id)
    }, current_app.config["JWT_SECRET_KEY"])

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

    # the verification code will be generated between 1234 and 9876
    code = randint(1234, 9876)

    if os.environ.get("FLASK_ENV") == "production":
        # send the verification code through sms only in production environment
        sms_response = requests.get(current_app.config["SMS_BASE_URL"], params={
            "route": "otp",
            "authorization": current_app.config["SMS_AUTHORIZATION"],
            "variables_values": code,
            "flash": 0,
            "numbers": mobile_number
        })
        response = sms_response.json()

        if response.get("return") is False:
            print(response.get("message"))
    else:
        # print the verification code in console in development environment
        print(f"verification code = {code}")

    current_time = datetime.now(UTC)

    # after 3 minutes verification code will be expired
    expires_at = str(
        current_time + timedelta(minutes=int(current_app.config["VERIFICATION_CODE_EXPIRES"])))

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
def update_mobile():
    data = request.get_json()
    user_id = g.user_data.get("_id")

    result = db.get_collection("users").update_one({
        "_id": ObjectId(user_id),
    }, {
        "$set": {
            "mobile_number": data.get("mobile_number")
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


@exception_handler
def update_name():
    user_id = g.user_data.get("_id")
    data = Validator(request.get_json()).field("first_name").required(
        "please enter your name").field("last_name").required("please enter the last name").execute()

    result = db["users"].update_one({
        "_id": ObjectId(user_id)
    }, {
        "$set": {
            "first_name": data.get("first_name"),
            "last_name": data.get("last_name")
        }
    })

    if result.matched_count < 1:
        return jsonify({
            "status": "fail",
            "message": "user not found"
        }), 404

    if result.modified_count < 1:
        return jsonify({
            "status": "fail",
            "message": "failed to updated"
        }), 400

    return jsonify({
        "status": "success",
        "message": "your name is updated"
    })


@exception_handler
def update_location():
    user_id = g.user_data.get("_id")
    data = Validator(request.get_json()).field("lat").required(
        "please enter your name").field("lng").required("please enter the last name").execute()

    result = db["users"].update_one({
        "_id": ObjectId(user_id)
    }, {
        "$set": {
            "location": {
                "type": "Point",
                "coordinates": [data.get("lat"), data.get("lng")]
            }
        }
    })

    if result.matched_count < 1:
        return jsonify({
            "status": "fail",
            "message": "user not found"
        }), 404

    if result.modified_count < 1:
        return jsonify({
            "status": "fail",
            "message": "failed to updated"
        }), 400

    return jsonify({
        "status": "success",
        "message": "location is updated"
    })
