import re
from functools import wraps
from flask import request, jsonify
from .validator import ValidationError


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
