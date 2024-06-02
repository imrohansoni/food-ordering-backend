from datetime import datetime, timezone

from bson import ObjectId
from flask import jsonify, request

from services.image_service import upload_images
from utils.validator import Validator
from utils.methods import create_slug, exception_handler
from database.db import db


@exception_handler
def create_product():
    data = (Validator(request.form.to_dict())
            .field("name")
            .required("Please enter the product name")
            .field("description")
            .field("category_id")
            .required("Please provide the category id")
            .field("type")
            .required("Please select the product type")
            .field("restaurant_id")
            .required("please provide the restaurant id")
            .execute())

    category = db["categories"].find_one({
        "_id": ObjectId(data["category_id"])
    }, projection={"_id": 1, "name": 1})

    if category is None:
        return jsonify({
            "status": "fail",
            "message": "category not found"
        }), 404

    data["category_id"] = ObjectId(category["_id"])
    data["name"] = ObjectId(category["name"])
    utc_now = datetime.now(timezone.utc)

    result = db["products"].insert_one({
        **data,
        "slug": create_slug(data["name"]),
        "res_name": "",
        "address": {},
        "created_at": utc_now,
        "last_updated_at": utc_now,
        "active": False
    })

    return jsonify({
        "status": "success",
        "data": {
            "productId": str(result.inserted_id)
        }
    }), 201


@exception_handler
def get_products():
    # todo: implement sorting, pagination, limiting, filtering
    products = list(db["products"].find())

    for product in products:
        product["_id"] = str(product["_id"])
        product["category_id"] = str(product["category_id"])

    return jsonify({
        "status": "success",
        "data": {
            "length": products.__len__(),
            "products": products
        }
    })


@exception_handler
def delete_product(product_id):
    result = db["products"].delete_one({
        "_id": ObjectId(product_id)
    })

    return jsonify({
        "status": "success",
        "message": "product is delete"
    }), 200


@exception_handler
def update_product(product_id):
    data = (Validator(request.form.to_dict())
            .field("name")
            .field("description")
            .field("category_id")
            .field("type")
            .field("customizable")
            .execute())

    if data.get("name") is not None:
        data["slug"] = create_slug(data["name"])

    result = db["products"].update_one({
        "_id": ObjectId(product_id)
    }, {
        "$set": {
            **data
        }
    })

    if result.matched_count < 1:
        return jsonify({
            "status": "fail",
            "message": "product not found"
        }), 404

    if result.modified_count < 1:
        return jsonify({
            "status": "fail",
            "message": "failed to update the product"
        }), 404

    return jsonify({
        "status": "success",
        "message": "product updated"
    })


@exception_handler
def add_product_images(product_id):
    data = (Validator(request.form.to_dict(), request.files)
            .file_field("product_images")
            .required("please provide the product images")
            .max_files(5, "maximum images can be uploaded")
            .is_image("please provide the valid images")
            .execute())

    uploaded_images = upload_images(data["product_images"], "products")

    result = db["products"].update_one({
        "_id": ObjectId(product_id)
    }, {
        "$push": {
            "product_images": {
                "$each": uploaded_images,
            },
        },
    })

    if result.matched_count < 1:
        return jsonify({
            "status": "success",
            "message": "product not found"
        }), 404

    return jsonify({
        "status": "success",
        "message": "product images is updated"
    }), 200


@exception_handler
def delete_single_product_image(product_id, product_image_id):
    result = db["products"].update_one({
        "_id": ObjectId(product_id),
    }, {
        "$pull": {
            "product_images": {
                "image_id": product_image_id
            }
        }
    })

    if result.matched_count < 1:
        return jsonify({
            "status": "fail",
            "message": "product images not found"
        }), 404

    if result.modified_count < 1:
        return jsonify({
            "status": "fail",
            "message": "product images not found"
        }), 404

    return jsonify({
        "status": "success",
        "message": "product image deleted"
    })


@exception_handler
def delete_multiple_product_images(product_id):
    result = db["products"].update_one({
        "_id": ObjectId(product_id),
    }, {
        "$pull": {
            "product_images": {
                # "image_id": product_image_id
            }
        }
    })

    if result.matched_count < 1:
        return jsonify({
            "status": "fail",
            "message": "product images not found"
        }), 404

    if result.modified_count < 1:
        return jsonify({
            "status": "fail",
            "message": "product images not found"
        }), 404

    return jsonify({
        "status": "success",
        "message": "product image deleted"
    })
