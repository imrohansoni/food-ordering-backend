from database import db
from flask import g, request, jsonify
from utils.validator import Validator
from datetime import datetime, UTC
from bson import ObjectId
from utils.methods import create_slug
from services.image_service import upload_images


def save_res_basic_details():
    data = (Validator(request.form.to_dict())
            .field("res_name")
            .required("Please enter your restaurant's name")
            .field("res_type")
            .required("Please select your restaurant's type")
            .field("address")
            .required("please provide your restaurant's address")
            .field("state")
            .required("state name is required")
            .field("city")
            .required("city name is required")
            .field("pin_code")
            .required("pin code is required")
            .field("lat")
            .required("please provide the latitude")
            .field("long")
            .required("please provide the longitude")
            .field("res_contact_number")
            .required("Please enter your restaurant's contact number")
            .field("res_email")
            .required("Please enter your restaurant's email")
            .field("owner_name")
            .required("Please enter the owner's name")
            .field("owner_mobile_number")
            .required("Please enter the owner's mobile number")
            .field("owner_email")
            .required("Please enter the owner's email")
            .execute())

    slug = create_slug(data["res_name"])

    lat = data["lat"]
    long = data["long"]

    location = {
        "type": "Point",
        "coordinates": [lat, long]
    }

    data["res_address"] = {
        "address": data["address"],
        "state": data["state"],
        "city": data["city"],
        "pin_code": data["pin_code"],
        "location": location
    }

    del data["address"]
    del data["state"]
    del data["city"]
    del data["pin_code"]
    del data["lat"]
    del data["long"]

    result = db["restaurants"].insert_one({
        **data,
        "slug": slug,
        "active": False,
        "last_updated_at": datetime.now(UTC),
        "created_at": datetime.now(UTC),
        "created_by": g.user_data.get("_id"),
    })

    res_id = str(result.inserted_id)

    return jsonify({
        "status": "success",
        "data": {
            "res_id": res_id
        }
    })


def save_res_timing():
    data = (Validator(request.form.to_dict())
            .field("res_id")
            .required("restaurant id is required")
            .field("opening_time")
            .required("Please provide your restaurant's opening time")
            .field("closing_time")
            .required("Please provide your restaurant's closing time")
            .field("open_days")
            .required("Please select open days")
            .is_list("open days must be a list")
            .execute())

    result = db["restaurants"].update_one(
        {
            "_id": ObjectId(data["res_id"]),
            "owner_id": g.user_data.get("_id")
        }, {
            "$set": {
                **data,
                "updated_at": datetime.now(UTC)
            }
        })

    if not result.matched_count > 0:
        return jsonify({
            "status": "fail",
            "message": "restaurant not found"
        }), 404

    return jsonify({
        "status": "fail",
        "message": "timing is added to the restaurant"
    })


def save_res_images():
    data = (Validator(request.form.to_dict(), request.files)
            .field("restaurant_id")
            .required("please provide the restaurant id")
            .file_field("res_images")
            .required("please provide the restaurant images")
            .max_files(5, "maximum images can be uploaded")
            .is_image("please provide the valid images")
            .execute())

    uploaded_images = upload_images(data["res_images"], "restaurants")

    result = db["restaurants"].update_one({
        "_id": ObjectId(data["restaurant_id"])
    }, {
        "$push": {
            "res_images": {
                "$each": uploaded_images,
            },
        },
    })

    if result.matched_count < 1:
        return jsonify({
            "status": "success",
            "message": "restaurant not found"
        }), 404

    return jsonify({
        "status": "success",
        "message": "restaurant images is updated"
    }), 200


def get_restaurants():
    owner_id = g.user_data.get("_id")
    restaurants = list(db["restaurants"].find({
        "owner_id": owner_id
    }))

    for res in restaurants:
        res["_id"] = str(res["_id"])

    return jsonify({
        "status": "success",
        "data": {
            "size": restaurants.__len__(),
            "restaurants": restaurants
        }
    })


def delete_restaurant(restaurant_id):
    result = db["restaurants"].delete_one({
        "_id": ObjectId(restaurant_id),
        "owner_id": g.user_data.get("_id")
    })

    if not result.deleted_count > 0:
        return jsonify({
            "status": "fail",
        }), 500

    return jsonify({
        "status": "success"
    })


def update_restaurant(restaurant_id):
    validator = (Validator(request.get_json())
                 .field("name")
                 .field("type")
                 .field("address")
                 .field("location")
                 .field("contact_number")
                 .field("restaurant_email")
                 .field("owner_name")
                 .field("owner_mobile_number")
                 .field("owner_email")
                 .field("opening_hour")
                 .field("closing_hour")
                 .field("open_days"))

    result = db["restaurants"].update_one({
        "_id": ObjectId(restaurant_id),
        "owner_id": request.user_data.get("owner_id")
    }, {
        "$set": validator.data
    })

    return jsonify({
        "status": "success",
        "message": "restaurant updated successfully"
    })


def get_single_restaurant(restaurant_id):
    restaurant = db["restaurants"].find_one({
        "_id": ObjectId(restaurant_id),
        "owner_id": request.user_data.get("owner_id")
    })

    if restaurant is None:
        return jsonify({
            "status": "fail",
            "message": "restaurant not found"
        })

    restaurant["_id"] = str(restaurant["_id"])

    return jsonify({
        "status": "success",
        "data": {
            "restaurant": restaurant
        }
    })


def get_restaurants_near_me():
    latitude = float(request.args.get('lat'))
    longitude = float(request.args.get('long'))
    distance = int(request.args.get('distance'))

    query_point = {
        "type": "Point",
        "coordinates": [latitude, longitude]
    }

    restaurants = list(db["restaurants"].find({
        "location": {
            "$near": {
                "$geometry": query_point,
                "$maxDistance": distance
            }
        }
    }))

    for res in restaurants:
        res["_id"] = str(res["_id"])

    return jsonify({
        "status": "success",
        "data": {
            "size": restaurants.__len__(),
            "restaurants": restaurants
        }
    }), 200
