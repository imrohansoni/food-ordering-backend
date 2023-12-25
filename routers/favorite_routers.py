from flask import Blueprint
from decorators.auth_decorators import authorize
from controllers.favorite_controllers import get_all_my_favorite, remove_from_favorite, add_to_favorite

favorite_bp = Blueprint("favorites", __name__)


@favorite_bp.get("/")
@authorize
def get_all_my_favorite_route():
    return get_all_my_favorite()


@favorite_bp.post("/")
@authorize
def add_to_favorite_route():
    return add_to_favorite()


@favorite_bp.delete("/")
@authorize
def remove_from_favorite_route():
    return remove_from_favorite()
