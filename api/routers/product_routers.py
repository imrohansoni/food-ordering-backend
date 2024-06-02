from controllers.product_controllers import create_product, delete_product, get_products, update_product, add_product_images, delete_multiple_product_images, delete_single_product_image


# from controllers.product_option_controllers import create_option_group, create_option, delete_option, update_option, get_options
from decorators.auth_decorators import authorize, access_permission
from flask import Blueprint
from utils.constants import UserTypes

product_bp = Blueprint("products", __name__)
product_admin_bp = Blueprint("products_admin", __name__)


# GET api/v1/products
@product_bp.get("/")
@authorize
def get_product_route():
    return get_products()


# POST api/v1/admin/products
@product_admin_bp.post("/")
@authorize
@access_permission(UserTypes.ADMIN.value)
def create_product_route():
    return create_product()


# PATCH api/v1/admin/products/123
@product_admin_bp.patch("/<string:product_id>")
@authorize
@access_permission(UserTypes.ADMIN.value)
def update_product_route(product_id):
    return update_product(product_id)


# DELETE api/v1/admin/products/123
@product_admin_bp.delete("/<string:product_id>")
@authorize
@access_permission(UserTypes.ADMIN.value)
def delete_product_route(product_id):
    return delete_product(product_id)


# api/v1/admin/products/123/images
@product_admin_bp.post("<string:product_id>/images")
@authorize
@access_permission(UserTypes.ADMIN.value)
def add_product_images_route(product_id):
    return add_product_images(product_id)


@product_admin_bp.delete("<string:product_id>/images/<string:product_image_id>")
@authorize
@access_permission(UserTypes.ADMIN.value)
def delete_single_product_image_route(product_id, product_image_id):
    return delete_single_product_image(product_id, product_image_id)


# # api/v1/admin/products/123/images/653
@product_admin_bp.delete("<string:product_id>/images/<string:product_image_id>")
@authorize
@access_permission(UserTypes.ADMIN.value)
def delete_multiple_product_image_route(product_id, product_image_id):
    return delete_multiple_product_images(product_id, product_image_id)


# # POST api/v1/admin/products/123/options
# @product_admin_bp.post("<string:product_id>/options")
# @authorize
# @access_permission(UserTypes.ADMIN.value)
# def create_option_group_route(product_id):
#     return create_option_group(product_id)

# # POST api/v1/admin/products/123/options


# @product_admin_bp.post("<string:product_id>/options")
# @authorize
# @access_permission(UserTypes.ADMIN.value)
# def create_option_group_route(product_id):
#     return create_option_group(product_id)


# # PATCH api/v1/admin/products/123/options/1
# @product_bp.post("<string:product_id>/options")
# @authorize
# @access_permission(UserTypes.ADMIN.value)
# def create_option_route(product_id):
#     return create_option(product_id)


# # DELETE api/v1/admin/products/123/options/1
# @product_bp.delete("<string:product_id>/options/<string:option_id>")
# @authorize
# @access_permission(UserTypes.ADMIN.value)
# def delete_option_route(product_id, option_id):
#     return delete_option(product_id, option_id)


# @product_bp.patch("<string:product_id>/options/<string:option_id>")
# @authorize
# @access_permission(UserTypes.ADMIN.value)
# def update_option_route(product_id, option_id):
#     return update_option(product_id, option_id)


# @product_bp.get("<string:product_id>/options")
# @authorize
# def get_options_route(product_id):
#     return get_options(product_id)
