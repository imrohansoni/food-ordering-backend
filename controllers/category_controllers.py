from bson import ObjectId
from flask import json, jsonify, request
from utils.validator import Validator
from database.db import db
from datetime import datetime, UTC
from utils.methods import exception_handler


@exception_handler
def create_category():
    validator = (Validator(request.get_json())
                 .field("category_name")
                 .required("please enter the category name")
                 .field("description")
                 .required("please enter the description of the category")
                 .execute())

    result = db.get_collection("categories").insert_one({
        **validator,
        "created_at": datetime.now(UTC)
    })

    inserted_id = result.inserted_id

    return jsonify({
        "status": "success",
        "data": {
            "category_id": str(inserted_id)
        }
    })


@exception_handler
def get_categories():
    categories = list(db.get_collection("categories").find())

    for category in categories:
        category["_id"] = str(category.get("_id"))

    return jsonify({
        "status": "success",
        "data": {
            "categories": categories
        }
    }), 200


@exception_handler
def delete_category(category_id):
    result = db.get_collection("categories").delete_one({
        "_id": ObjectId(category_id)
    })

    if result.deleted_count < 1:
        return jsonify({
            "status": "fail",
            "message": "failed to delete the category"
        }), 404

    return jsonify({
        "status": "success",
        "message": "category is deleted"
    })


@exception_handler
def update_category(category_id):
    validator = Validator(request.get_json()).field(
        "category_name").field("description").execute()

    result = db.get_collection("categories").update_one({
        "_id": ObjectId(category_id)
    }, {
        "$set": {
            **validator
        }
    })

    if result.matched_count < 1:
        return jsonify({
            "status": "fail",
            "message": "category not found"
        }), 404

    return jsonify({
        "status": "success",
        "message": "category is updated"
    }), 200
