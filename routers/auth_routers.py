from flask import Blueprint
from controllers.auth_controllers import login_admin, reset_password, send_code, login, change_password, send_password_reset_token
from decorators.auth_decorators import access_permission, authorize, verify_admin_account, verify_code, check_mobile_number
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


@auth_bp.post("/admin/change-password")
@authorize
@access_permission(UserTypes.ADMIN.value)
def change_password_route():
    return change_password()


@auth_bp.post("/admin/forgot-password")
@verify_admin_account
def forgot_password_route():
    return send_code()


@auth_bp.post("/admin/password-reset-token")
@verify_code
def password_reset_token_route():
    return send_password_reset_token()


@auth_bp.post("/admin/reset-password")
def reset_password_route():
    return reset_password()


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
