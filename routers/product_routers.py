from controllers.product_controllers import create_product, get_products
from controllers.product_option_controllers import create_option_group, create_option, delete_option, update_option, get_options
from decorators.auth_decorators import authorize, access_permission
from flask import Blueprint
from utils.constants import UserTypes

product_blueprint = Blueprint("products", __name__)


@product_blueprint.post("/")
@authorize
@access_permission(UserTypes.ADMIN.value)
def create_product_route():
    return create_product()


@product_blueprint.get("/")
@authorize
def get_product_route():
    return get_products()


@product_blueprint.post("<string:product_id>/option-group")
@authorize
@access_permission(UserTypes.ADMIN.value)
def create_option_group_route(product_id):
    return create_option_group(product_id)


@product_blueprint.post("<string:product_id>/options")
@authorize
@access_permission(UserTypes.ADMIN.value)
def create_option_route(product_id):
    return create_option(product_id)


@product_blueprint.delete("<string:product_id>/options/<string:option_id>")
@authorize
@access_permission(UserTypes.ADMIN.value)
def delete_option_route(product_id, option_id):
    return delete_option(product_id, option_id)


@product_blueprint.patch("<string:product_id>/options/<string:option_id>")
@authorize
@access_permission(UserTypes.ADMIN.value)
def update_option_route(product_id, option_id):
    return update_option(product_id, option_id)


@product_blueprint.get("<string:product_id>/options")
@authorize
def get_options_route(product_id):
    return get_options(product_id)
