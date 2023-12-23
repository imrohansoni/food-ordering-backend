from bson import ObjectId
from flask import jsonify, request
from services.image_service import upload_images
from utils.validator import Validator
from utils.methods import create_slug, exception_handler
from database.db import db
from datetime import datetime, UTC


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
            .field("customizable")
            .default_value(False))

    if not data.data.get("customizable"):
        data = (data
                .field("price")
                .required("Please enter the price")
                .field("discount")
                .default_value(0)
                .execute())
    else:
        data = data.execute()

    category = db.get_collection("categories").find_one({
        "_id": ObjectId(data.get("category_id"))
    }, projection={"_id": 1})

    if category is None:
        return jsonify({
            "status": "fail",
            "message": "category not found"
        }), 404

    data["category_id"] = ObjectId(data.get("category_id"))

    result = db.get_collection("products").insert_one({
        **data,
        "slug": create_slug(data.get("name")),
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
def set_product_images(product_id):
    data = (Validator(request.form.to_dict(), request.files)
            .file_field("product_images")
            .required("please provide the product images")
            .max_files(5, "maximum images can be uploaded")
            .is_image("please provide the valid images")
            .execute())

    uploaded_images = upload_images(data.get("product_images"), "products")

    result = db.get_collection("products").update_one({
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
            "message": "failed to update the product images"
        })

    return jsonify({
        "status": "success",
        "message": "product images is updated"
    })


@exception_handler
def remove_product_image(product_id, product_image_id):
    result = db.get_collection("products").update_one({
        "_id": ObjectId(product_id),
    }, {
        "$pull": {
            "product_images": {
                "_id": ObjectId(product_image_id)
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
def get_products():
    products = list(db.get_collection("products").find())

    for product in products:
        print(product)
        product["_id"] = str(product.get("_id"))
        product["category_id"] = str(product.get("category_id"))

    return jsonify({
        "status": "success",
        "data": {
            "length": products.__len__(),
            "products": products
        }
    })


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
        data["slug"] = create_slug(data.get("name"))

    result = db.get_collection("products").update_one({
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
