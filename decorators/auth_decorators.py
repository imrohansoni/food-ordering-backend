from functools import wraps
from utils.methods import exception_handler
from flask import g, jsonify, request
from database.db import db
from bson import ObjectId
import os
from jsonwebtoken import decode, encode


@exception_handler
def authorize(handler):
    @wraps(handler)
    def decorator_fun(*args, **kwargs):
        authorization = request.headers.get("authorization")

        if authorization is None or not authorization.startswith("Bearer"):
            return jsonify({
                "status": "fail",
                "message": "please login"
            }), 401

        token = authorization.split(" ")[1]
        if token is None:
            return jsonify({
                "status": "fail",
                "message": "token not found"
            }), 401

        decoded_token = decode(token, os.environ.get(
            "JWT_SECRET_KEY"), algorithms=["HS256"])

        user_id = decoded_token.get("user_id")

        user = db.get_collection("users").find_one({
            "_id": ObjectId(user_id)
        })

        if user is None:
            return jsonify({
                "status": "fail",
                "message": "user not found"
            }), 401

        g.user_data = user
        return handler(*args, **kwargs)

    return decorator_fun


@exception_handler
def access_permission(authorized_users: list):
    def decorated_wrapper(handler):
        @wraps(handler)
        def decorated_fun(*args, **kwargs):
            current_user_type = request.user_data.get("user_type")
            if current_user_type not in authorized_users:
                return jsonify({
                    "status": "fail",
                    "message": "you can not access this route"
                }), 401

            return handler(*args, **kwargs)

        return decorated_fun

    return decorated_wrapper
