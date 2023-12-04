from controllers.product_controllers import create_product, create_option_group, create_option, delete_option, get_products
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
