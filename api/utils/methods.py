import re
from functools import wraps
import traceback
from flask import jsonify
from .validator import ValidationError
import json
import os
from hashlib import sha256
from utils.constants import Environment


def generate_hash(data):
    json_data = json.dumps({
        **data
    }, sort_keys=True) + os.environ.get("HASH_SECRET")

    hash_string = sha256(json_data.encode()).hexdigest()
    return hash_string


def exception_handler(handler):
    @wraps(handler)
    def decorator_fun(*args, **kwargs):
        try:
            return handler(*args, **kwargs)
        except ValidationError as e:
            print(e)
            return jsonify({
                "status": "fail",
                "errors": e.errors
            }), 400
        except Exception as e:
            print(e)
            traceback.print_exc()

            if os.environ.get("FLASK_ENV") == Environment.DEVELOPMENT.value:
                return jsonify({
                    "stack": traceback.print_stack(),
                    "status": "fail",
                    "errors": str(e)
                }), 400

            return jsonify({
                "status": "fail",
                "errors": str(e)
            }), 400

    return decorator_fun


def create_slug(input_string):
    lowercase_string = input_string.lower()
    slug = re.sub(r'\s+', '-', lowercase_string)
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug
