from controllers.product_controllers import create_product, get_products, set_product_images, remove_product_image
from controllers.product_option_controllers import create_option_group, create_option, delete_option, update_option, get_options
from decorators.auth_decorators import authorize, access_permission
from flask import Blueprint
from utils.constants import UserTypes

product_bp = Blueprint("products", __name__)


@product_bp.post("/")
@authorize
@access_permission(UserTypes.ADMIN.value)
def create_product_route():
    return create_product()


@product_bp.post("<string:product_id>/product-images")
@authorize
@access_permission(UserTypes.ADMIN.value)
def set_product_images_route(product_id):
    return set_product_images(product_id)


@product_bp.delete("<string:product_id>/product-images/<string:product_image_id>")
@authorize
@access_permission(UserTypes.ADMIN.value)
def remove_product_image_route(product_id, product_image_id):
    return remove_product_image(product_id, product_image_id)


@product_bp.get("/")
@authorize
def get_product_route():
    return get_products()


@product_bp.post("<string:product_id>/option-group")
@authorize
@access_permission(UserTypes.ADMIN.value)
def create_option_group_route(product_id):
    return create_option_group(product_id)


@product_bp.post("<string:product_id>/options")
@authorize
@access_permission(UserTypes.ADMIN.value)
def create_option_route(product_id):
    return create_option(product_id)


@product_bp.delete("<string:product_id>/options/<string:option_id>")
@authorize
@access_permission(UserTypes.ADMIN.value)
def delete_option_route(product_id, option_id):
    return delete_option(product_id, option_id)


@product_bp.patch("<string:product_id>/options/<string:option_id>")
@authorize
@access_permission(UserTypes.ADMIN.value)
def update_option_route(product_id, option_id):
    return update_option(product_id, option_id)


@product_bp.get("<string:product_id>/options")
@authorize
def get_options_route(product_id):
    return get_options(product_id)
