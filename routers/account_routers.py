from flask import Blueprint

from controllers.account_controllers import get_account, update_location, update_name
from decorators.auth_decorators import authorize

account_bp = Blueprint("account", __name__)


@account_bp.get("/")
@authorize
def get_account_route():
    return get_account()


@account_bp.patch("/name")
@authorize
def update_name_route():
    return update_name()


@account_bp.patch("/location")
@authorize
def update_location_route():
    return update_location()
