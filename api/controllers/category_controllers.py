from bson import ObjectId
from flask import jsonify, request
from services.image_service import upload_images
from database.db import get_db
from datetime import datetime, timezone
from utils.validator import Validator
from utils.methods import exception_handler


@exception_handler
def create_category():
    db = get_db()
    data = (Validator(request.form.to_dict(), request.files)
            .field("name")
            .required("please enter the category name")
            .is_string("category name must be a string")
            .range_length(6, 25, "category name must be between 6 and 25 characters in length")
            .field("description")
            .required("please enter the description of the category")
            .is_string("description must be a string")
            .max_length(400, "description must be less than 400 characters")
            .file_field("category_image")
            .required("please provide the category image")
            .is_image("please provide the image files")
            .execute())

    category = db.get_collection("categories").find_one({
        "name": data.get("name")
    }, projection={
        "name": 1
    })

    if category is not None:
        return jsonify({
            "status": "fail",
            "message": f"{category['name']} is not already exits"
        })

    uploaded_image = upload_images(
        data.get("category_image"), "categories")

    del data["category_image"]

    utc_now = datetime.now(timezone.utc)

    result = db.get_collection("categories").insert_one({
        **data,
        **uploaded_image[0],
        "created_at": utc_now,
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
    db = get_db()
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
    db = get_db()
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
    db = get_db()
    validator = (Validator(request.get_json())
                 .field("category_name")
                 .field("description")
                 .execute())

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
