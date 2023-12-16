import cloudinary
from bson import ObjectId
from flask import json, jsonify, request, current_app
from utils.validator import Validator, ValidationError
from database.db import db
from datetime import datetime, UTC
from utils.methods import exception_handler
from cloudinary.utils import cloudinary_url
from cloudinary.uploader import upload
import uuid


@exception_handler
def create_category():
    data = (Validator(request.form.to_dict())
            .field("name")
            .required("please enter the category name")
            .is_string("category name must be a string")
            .validate(lambda value: len(value) <= 24, "category name must be less then or equal to 24 letters")
            .field("description")
            .required("please enter the description of the category")
            .is_string("description must be a string")
            .validate(lambda value: len(value) <= 400, "category name must be less then or equal to 24 letters")
            .execute())

    if not "category_image" in request.files:
        return jsonify({
            "status": "fail",
            "message": "please provide the category image"
        }), 400

    category_image = request.files["category_image"]

    if category_image.filename == "":
        return jsonify({
            "status": "fail",
            "message": "please provide the category image"
        }), 400

    category = db.get_collection("categories").find_one({
        "name": data.get("name")
    }, projection={
        "name": 1
    })

    code = str(uuid.uuid4()).replace("-", "")
    upload_result = upload(category_image,
                           public_id=f"{code}{data.get('name')}",
                           overwrite=True,
                           folder="categories")

    image_url, options = cloudinary_url(upload_result['public_id'],
                                        format=upload_result['format'])

    result = db.get_collection("categories").insert_one({
        **data,
        "category_image_url": image_url,
        "image_public_id": upload_result["public_id"],
        "created_at": datetime.now(UTC),
        "active": True
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
