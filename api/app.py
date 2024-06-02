import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import cloudinary
from utils.constants import Environment
from database.db import connect


from routers.auth_routers import auth_bp
from routers.product_routers import product_bp
from routers.product_routers import product_admin_bp
from routers.category_routers import category_bp
from routers.account_routers import account_bp
from routers.favorite_routers import favorite_bp

app = Flask(__name__)

load_dotenv()

config = cloudinary.config(
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
)

app.register_blueprint(product_bp, url_prefix="/api/v1/products")
app.register_blueprint(product_admin_bp, url_prefix="/api/v1/admin/products")
app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
app.register_blueprint(category_bp, url_prefix="/api/v1/categories")
app.register_blueprint(account_bp, url_prefix="/api/v1/account")
app.register_blueprint(favorite_bp, url_prefix="/api/v1/favorites")


@app.route("/test")
def test():
    return jsonify({
        "status": "success",
        "data": "server is working successfully"
    })


@app.errorhandler(404)
def page_not_found(error):
    print(error)
    return jsonify({
        "status": "fail",
        "message": f"{request.path} is not found"
    }), 404


@app.errorhandler(405)
def method_not_found(error):
    print(error)
    return jsonify({
        "status": "fail",
        "message": f"{request.method} is not defined on {request.path}"
    }), 405


@app.errorhandler(Exception)
def handle_exception(error):
    print(error)
    return jsonify({
        "status": "error",
        "message": "something went wrong"
    }), 500



# update name
# update email
# update mobile number
# save location
# send notifications


if __name__ == "__main__":
    flask_env = os.environ.get("FLASK_ENV")

    if flask_env is None:
        print("Server is running without any environment ⛔")
    else:
        print(f"Server is running in {flask_env} environment 🚀")

    connect()
    if flask_env == Environment.DEVELOPMENT.value:
        app.run(host="0.0.0.0", port=5000, debug=True, load_dotenv=True)
    else:
        app.run(host="0.0.0.0")
