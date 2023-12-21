from flask import Blueprint
from controllers.auth_controllers import forgot_password, login_admin, send_code, login, change_password
from decorators.auth_decorators import access_permission, authorize, verify_code, check_mobile_number
from controllers.account_controllers import update_mobile
from utils.constants import UserTypes

auth_bp = Blueprint("authentications", __name__)


@auth_bp.post("/send-code")
def send_code_route():
    return send_code()


@auth_bp.post("/login")
@verify_code
def login_route():
    return login()


@auth_bp.post("/admin/login")
def login_admin_route():
    return login_admin()


@auth_bp.post("/admin/forgot-password")
def forgot_password_route():
    return forgot_password()


@auth_bp.post("/admin/change-password")
@authorize
@access_permission(UserTypes.ADMIN.value)
def change_password_route():
    return change_password()


@auth_bp.post("/update-mobile/send-code")
@authorize
@check_mobile_number
def update_mobile_send_code_route():
    return send_code()


@auth_bp.post("/update-mobile")
@authorize
@verify_code
def update_mobile_route():
    return update_mobile()
