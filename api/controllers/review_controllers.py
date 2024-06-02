from bson import ObjectId
from flask import request, g, jsonify
from database.db import db
from utils.validator import Validator


def create_review(product_id):
    user_id = g.user_data.get("_id")

    validator = (Validator(request.get_json())
                 .field("rating")
                 .required("please choose your rating")
                 .field("review")
                 .execute())

    product = db.get_collection("products").find_one({
        "_id": ObjectId(product_id)
    }, projection={
        "_id": 1
    })

    if product is None:
        return jsonify({
            "status": "fail",
            "message": "product is not available"
        }), 404

    db.get_collection("reviews").insert_one({
        "user_id": str(user_id),
        "product_id": product.get("_id"),
    })
