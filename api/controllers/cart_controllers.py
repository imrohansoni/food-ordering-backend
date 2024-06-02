from collections import UserDict
from bson import ObjectId
from flask import jsonify, request, g
from utils.validator import Validator
from database.db import db
from datetime import datetime, UTC


def get_cart_items():
    user_id = g.user_data.get("_id")
    result = db.get_collection("carts").find({
        "user_id": ObjectId(user_id)
    })


def add_to_cart():
    user_id = g.user_data.get("_id")
    validator = (Validator(request.get_json())
                 .field("product_id")
                 .required("Please provide the product id")
                 .field("quantity")
                 .required("Please provide the product quantity")
                 .execute())

    # user_id, product_id

    db.get_collection("carts").insert_one({
        "user_id": user_id,
        "product_id": ObjectId(validator.get("product_id")),
        "quantity": validator.get("quantity"),
        "created_at": datetime(UTC)
    })


def remove_from_cart():
    user_id = g.user_data.get("_id")
    validator = (Validator(request.get_json())
                 .field("product_id")
                 .required("Please provide the product id")
                 .field("quantity")
                 .required("Please provide the product quantity")
                 .execute())

    result = db.get_collection("cart").insert_one({
        "user_id": str(user_id),
        **validator
    })


def update_cart_items():
    user_id = g.user_data.get("_id")
    validator = (Validator(request.get_json())
                 .field("product_id")
                 .required("Please provide the product id")
                 .field("quantity")
                 .required("Please provide the product quantity")
                 .execute())

    result = db.get_collection("cart").insert_one({
        "user_id": str(user_id),
        **validator
    })
