from flask import Blueprint
from controllers.auth_controllers import send_code, verify_code, login, check_mobile_number, update_mobile
from decorators.auth_decorators import authorize

auth_blueprint = Blueprint("authentications", __name__)


@auth_blueprint.post("/send-code")
def send_code_route():
    return send_code()


@auth_blueprint.post("/login")
@verify_code
def login_route():
    return login()


@auth_blueprint.post("/update-mobile/send-code")
@authorize
@check_mobile_number
def update_mobile_send_code_route():
    return send_code()


@auth_blueprint.post("/update-mobile")
@authorize
@verify_code
def update_mobile_route():
    return update_mobile()
