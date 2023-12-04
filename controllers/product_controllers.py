from math import prod
from bson import ObjectId
from flask import jsonify, request
from utils.validator import Validator
from utils.methods import create_slug, exception_handler
from database.db import db
from datetime import datetime, UTC


@exception_handler
def create_product():
    validator = (Validator(request.get_json())
                 .field("name")
                 .required("Please enter the product name")
                 .field("description")
                 .required("Please enter the description")
                 .field("category_id")
                 .required("Please provide the category id")
                 .field("type")
                 .required("Please select the product type")
                 .field("image_url")
                 .required("Please provide the image of the product")
                 .field("customizable")
                 .default_value(False))

    if not validator.data.get("customizable"):
        validator = (validator
                     .field("price")
                     .required("Please enter the price")
                     .field("discount")
                     .default_value(0)
                     .execute())
    else:
        validator = validator.execute()

    category = db.get_collection("categories").find_one({
        "_id": ObjectId(validator.get("category_id"))
    }, projection={"_id": 1})

    if category is None:
        return jsonify({
            "status": "fail",
            "message": "category not found"
        }), 404

    validator["category_id"] = ObjectId(validator.get("category_id"))

    result = db.get_collection("products").insert_one({
        **validator,
        "slug": create_slug(validator.get("name")),
        "created_at": datetime.now(UTC),
        "last_updated_at": datetime.now(UTC),
        "active": False
    })

    inserted_id = result.inserted_id

    return jsonify({
        "status": "success",
        "data": {
            "productId": str(inserted_id)
        }
    }), 201


@exception_handler
def get_products():
    # add filtering, sorting, pagination, limiting for the products
    products = list(db.get_collection("products").find())

    for product in products:
        product["_id"] = str(product.get("_id"))
        product["category_id"] = str(product.get("category_id"))

    return jsonify({
        "status": "success",
        "data": {
            "length": products.__len__(),
            "products": products
        }
    })
