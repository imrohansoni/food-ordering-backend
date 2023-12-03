import re
from functools import wraps
from flask import request, jsonify
from .validator import ValidationError
import json
import os
from hashlib import sha256


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
            return jsonify({
                "status": "fail",
                "errors": e.errors
            })
        except Exception as e:
            return jsonify({
                "status": "fail",
                "errors": str(e)
            })

    return decorator_fun


def create_slug(input_string):
    lowercase_string = input_string.lower()
    slug = re.sub(r'\s+', '-', lowercase_string)
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug
