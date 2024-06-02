from flask import Blueprint
from controllers.category_controllers import create_category, get_categories, delete_category, update_category
from decorators.auth_decorators import authorize, access_permission
from utils.constants import UserTypes

category_bp = Blueprint("categories", __name__)


@category_bp.post("/")
@authorize
@access_permission(UserTypes.ADMIN.value)
def create_category_route():
    return create_category()


@category_bp.get("/")
@authorize
def get_categories_route():
    return get_categories()


@category_bp.delete("/<string:category_id>")
@authorize
@access_permission(UserTypes.ADMIN.value)
def delete_category_route(category_id):
    return delete_category(category_id)


@category_bp.patch("<string:category_id>")
@authorize
@access_permission(UserTypes.ADMIN.value)
def update_category_route(category_id):
    return update_category(category_id)
