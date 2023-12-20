from math import prod
from bson import ObjectId
from flask import jsonify, request
from controllers.upload_controllers import ALLOWED_IMAGE_EXTENSIONS
from utils.validator import Validator
from utils.methods import create_slug, exception_handler
from database.db import db
from datetime import datetime, UTC
import os
import uuid
from cloudinary.utils import cloudinary_url
from cloudinary.uploader import upload


@exception_handler
def create_product():
    data = (Validator(request.form.to_dict())
            .field("name")
            .required("Please enter the product name")
            .field("description")
            .required("Please enter the description")
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
    product_images = request.files.getlist("product_images")

    if product_images.__len__() < 1:
        return jsonify({
            "status": "fail",
            "message": "please provide the images"
        })

    if product_images.__len__() > 5:
        return jsonify({
            "status": "fail",
            "message": "maximum of 5 images can be uploaded at once"
        })

    for img in product_images:
        if img.filename == "" or not "." in img.filename or not img.filename.rsplit(".", 1)[1].upper() in ALLOWED_IMAGE_EXTENSIONS:
            return jsonify({
                "status": "fail",
                "message": "image not provided or invalid extensions"
            }), 400

    uploaded_images = []

    for img in product_images:
        code = str(uuid.uuid4()).replace("-", "")

        if os.environ.get("FLASK_ENV") == "development":
            upload_folder = "uploads/products"

            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            image_filename = f"{code}{img.filename}"
            upload_path = os.path.join(upload_folder, image_filename)
            img.save(upload_path)

            uploaded_images.append({
                "_id": ObjectId(),
                "image_url": os.path.abspath(upload_path),
                "image_id": image_filename
            })

        else:
            upload_result = upload(img,
                                   public_id=f"{code}{img.filename}",
                                   overwrite=True,
                                   folder="categories")

            image_id = upload_result['public_id']
            image_url, _ = cloudinary_url(image_id,
                                          format=upload_result['format'])

            uploaded_images.append({
                "_id": ObjectId(),
                "image_url": image_url,
                "image_id": image_id
            })

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
        "status": "sucess",
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
