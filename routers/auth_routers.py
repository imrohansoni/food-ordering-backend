from flask import Blueprint
from controllers.auth_controllers import send_code, verify_code

auth_blueprint = Blueprint("authentications", __name__)


@auth_blueprint.post("/send-code")
def send_code_route():
    return send_code()


@auth_blueprint.post("/verify-code")
def verify_code_route():
    return verify_code()
