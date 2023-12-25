from bson import ObjectId
from flask import g, request, jsonify

from utils.validator import Validator
from database.db import db
from datetime import datetime, UTC


def add_to_favorite():
    user_id = g.user_data.get("_id")
    data = (Validator(request.get_json())
            .field("product_id")
            .required("please provide the product id")
            .execute())

    product = db["products"].find_one({
        "_id": ObjectId(data["product_id"])
    }, projection={
        "_id": 1
    })

    if product is None:
        return jsonify({
            "status": "success",
            "message": "product not found"
        }), 404

    db["favorites"].insert_one({
        "user_id": user_id,
        "product_id": product.get("_id"),
        "created_at": datetime.now(UTC)
    })

    return jsonify({
        "status": "success",
        "message": "item is added to the favorite list"
    })


def remove_from_favorite():
    user_id = g.user_data.get("_id")

    data = (Validator(request.get_json())
            .field("product_id")
            .required("please provide the product id")
            .execute())

    result = db["favorites"].delete_one({
        "product_id": ObjectId(data["product_id"]),
        "user_id": ObjectId(user_id)
    })

    if result is None:
        return jsonify({
            "status": "fail",
            "message": "product not found in your list"
        })

    return jsonify({
        "status": "success",
        "message": "product is removed from the favorite list"
    })


def get_all_my_favorite():
    user_id = g.user_data.get("_id")

    favorites = list(db["favorites"].find({
        "user_id": ObjectId(user_id)
    }))

    for fav in favorites:
        fav["_id"] = str(fav["_id"])
        fav["user_id"] = str(fav["user_id"])
        fav["product_id"] = str(fav["product_id"])

    return jsonify({
        "status": "success",
        "data": favorites
    })
