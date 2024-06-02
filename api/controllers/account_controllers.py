from datetime import datetime, timezone
from flask import request, g, jsonify
from bson import ObjectId, utc

from utils.validator import Validator
from utils.methods import exception_handler
from database.db import get_db


@exception_handler
def update_name():
    db = get_db()
    user_id = g.user_data.get("_id")
    print(request.get_json())
    data = (Validator(request.get_json())
            .field("first_name")
            .required("please enter your name")
            .field("last_name")
            .required("please enter the last name")
            .execute())
    utc_now = datetime.now(timezone.utc)

    result = db["users"].update_one({
        "_id": ObjectId(user_id),
        "active": True
    }, {
        "$set": {
            "first_name": data.get("first_name"),
            "last_name": data.get("last_name"),
            "last_updated_at": utc_now
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
        "data": "your name has been updated"
    })


@exception_handler
def update_location():
    db = get_db()
    user_id = g.user_data.get("_id")
    data = (Validator(request.get_json())
            .field("lat")
            .required("please enter the latitude")
            .field("long")
            .required("please enter the longitudes")
            .execute())
    print(data)

    utc_now = datetime.now(timezone.utc)

    result = db["users"].update_one({
        "_id": ObjectId(user_id),
        "active": True
    }, {
        "$set": {
            "location": {
                "type": "Point",
                "coordinates": [data.get("lat"), data.get("long")]
            },
            "last_updated_at": utc_now
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
            "message": "failed to updated your location"
        }), 400

    return jsonify({
        "status": "success",
        "data": "your location has been updated"
    })


@exception_handler
def update_mobile():
    db = get_db()
    data = request.get_json()
    user_id = g.user_data.get("_id")

    utc_now = datetime.now(timezone.utc)

    result = db["users"].update_one({
        "_id": ObjectId(user_id),
        "active": True
    }, {
        "$set": {
            "mobile_number": data.get("mobile_number"),
            "last_updated_at": utc_now
        }
    })

    if result.matched_count < 1:
        return jsonify({
            "status": "fail",
            "message": "user not found"
        }), 404
    return jsonify({
        "status": "success",
        "message": "your mobile number has been updated"
    })


@exception_handler
def get_account():
    user_data = g.user_data

    user_data["_id"] = str(user_data["_id"])

    return jsonify({
        "status": "success",
        "data": user_data
    }), 200


@exception_handler
def add_address():
    db = get_db()
    data = request.get_json()
    user_id = g.user_data.get("_id")

    data = (Validator(request.get_json())
            .field("detailed_address")
            .required("please fill this field")
            .field("city")
            .required("please provide the city name")
            .field("state")
            .required("please provide the state name")
            .field("district")
            .required("please provide the district name")
            .execute())

    result = db["users"].update_one(
        {
            "_id": ObjectId(user_id),
            "active": True
        },
        {
            "$push": {
                "addresses": {
                    **data
                }
            }
        }
    )

    return jsonify({
        "status": "success",
        "message": "address added"
    }), 200


@exception_handler
def update_email():
    db = get_db()
    user_id = g.user_data.get("_id")
    print(request.get_json())
    data = (Validator(request.get_json())
            .field("email")
            .required("please enter your email")
            .execute())
    
    utc_now = datetime.now(timezone.utc)

    result = db["users"].update_one({
        "_id": ObjectId(user_id),
        "active": True
    }, {
        "$set": {
            "email": data.get("email"),
            "last_updated_at": utc_now
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
        "data": "your email has been updated"
    })
