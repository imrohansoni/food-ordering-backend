from datetime import datetime, UTC
from utils.validator import Validator
from utils.methods import exception_handler
from flask import request, g, jsonify
from bson import ObjectId
from database.db import db


@exception_handler
def update_name():
    user_id = g.user_data.get("_id")
    data = Validator(request.get_json()).field("first_name").required(
        "please enter your name").field("last_name").required("please enter the last name").execute()

    result = db["users"].update_one({
        "_id": ObjectId(user_id)
    }, {
        "$set": {
            "name": [data.get("first_name"), data.get("last_name")],
            "last_updated_at": datetime.now(UTC)
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
            },
            "last_updated_at": datetime.now(UTC)
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


@exception_handler
def update_mobile():
    data = request.get_json()
    user_id = g.user_data.get("_id")

    result = db.get_collection("users").update_one({
        "_id": ObjectId(user_id),
        "active": True
    }, {
        "$set": {
            "mobile_number": data.get("mobile_number"),
            "last_updated_at": datetime.now(UTC)
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
def get_account():
    user_data = g.user_data

    user_data["_id"] = str(user_data["_id"])

    return jsonify({
        "status": "success",
        "data": user_data
    }), 200
