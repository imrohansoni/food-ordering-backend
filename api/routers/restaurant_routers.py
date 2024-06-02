from flask import Blueprint
from decorators.auth_decorators import authorize, access_permission

from controllers.restaurant_controllers import create_restaurant, add_restaurant_timing, add_restaurant_images, get_all_restaurants

from utils.constants import UserTypes

restaurant_blueprint = Blueprint("restaurants", __name__)


@restaurant_blueprint.post("/new-res/res-basic-details")
@authorize
def create_restaurant_route():
    return create_restaurant()


@restaurant_blueprint.post("/new-res/res-timing")
@authorize
def add_restaurant_timing_route():
    return add_restaurant_timing()


@restaurant_blueprint.post("/new-res/res-images")
@authorize
def add_restaurant_images_route():
    return add_restaurant_images()


@restaurant_blueprint.get("/")
@authorize
@access_permission(UserTypes.ADMIN.value)
def get_all_restaurants_route():
    return get_all_restaurants()
