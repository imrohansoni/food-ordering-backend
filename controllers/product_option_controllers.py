from utils.methods import exception_handler
from utils.validator import Validator
from flask import request, jsonify
from bson import ObjectId
from database.db import db


@exception_handler
def create_option_group(product_id):
    data = (Validator(request.get_json())
            .field("title")
            .required("Please enter the option group title")
            .field("sub_title")
            .field("type")
            .required("Please enter the option group type")
            .execute())

    result = db.get_collection("products").update_one({
        "_id": ObjectId(product_id),
        "customizable": True
    }, {
        "$set": {
            "option_group": {
                **data
            }
        }
    })

    if result.matched_count < 1:
        return jsonify({
            "status": "fail",
            "message": "no customizable product found"
        }), 404

    return jsonify({
        "status": "success",
        "message": "option group is created"
    })


@exception_handler
def create_option(product_id):
    validator = (Validator(request.get_json())
                 .field("value")
                 .required("Please provide the option value")
                 .field("price")
                 .required("Please provide the option price")
                 .field("discount")
                 .default_value(0)
                 .field("available")
                 .required("please provide the availability")
                 .execute())

    result = db.get_collection("products").update_one({
        "_id": ObjectId(product_id),
        "customizable": True
    }, {
        "$push": {
            "option_group.options": {
                "_id": ObjectId(),
                ** validator
            }
        }
    })

    if result.matched_count < 1:
        return jsonify({
            "status": "fail",
            "message": "no customizable product found"
        }), 404

    return jsonify({
        "status": "success",
        "message": "option is created"
    }), 200


@exception_handler
def delete_option(product_id, option_id):
    result = db.get_collection("products").update_one({
        "_id": ObjectId(product_id),
        "customizable": True
    }, {
        "$pull": {
            "option_group.options": {
                "_id": ObjectId(option_id)
            }
        }
    })

    if result.matched_count < 1:
        return jsonify({
            "status": "fail",
            "message": "no customizable product found"
        }), 404

    return jsonify({
        "status": "success",
        "message": "option is deleted"
    }), 200


@exception_handler
def update_option(product_id, option_id):
    validator = (Validator(request.get_json())
                 .field("value")
                 .field("price")
                 .field("discount")
                 .field("available")
                 .execute())

    update_values = {}

    for key in validator.keys():
        update_values[f"option_group.options.$.{key}"] = validator.get(key)

    result = db.get_collection("products").update_one({
        "_id": ObjectId(product_id),
        "option_group.options._id": ObjectId(option_id),
        "customizable": True
    }, {
        "$set": {
            **update_values
        }
    })

    if result.matched_count < 1:
        return jsonify({
            "status": "fail",
            "message": "no customizable product found"
        }), 404

    return jsonify({
        "status": "success",
        "message": "option is updated"
    }), 200


@exception_handler
def get_options(product_id):
    result = db["products"].find_one({
        "_id": ObjectId(product_id),
        "customizable": True
    }, projection={
        "option_group": 1
    })

    options = list(result.get("option_group").get("options"))

    for option in options:
        option["_id"] = str(option.get("_id"))

    return jsonify({
        "status": "success",
        "data": {
            "length": options.__len__(),
            "option": options
        }
    })
