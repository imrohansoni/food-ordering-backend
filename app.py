import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import cloudinary


from routers.auth_routers import auth_bp
from routers.product_routers import product_bp
from routers.category_routers import category_bp
from routers.account_routers import account_bp
from routers.favorite_routers import favorite_bp

load_dotenv()

app = Flask(__name__)

config = cloudinary.config(
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
)

app.register_blueprint(product_bp, url_prefix="/api/v1/products")
app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
app.register_blueprint(category_bp, url_prefix="/api/v1/categories")
app.register_blueprint(account_bp, url_prefix="/api/v1/account")
app.register_blueprint(favorite_bp, url_prefix="/api/v1/favorites")


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


environment = os.environ.get("FLASK_ENV")

if environment is None:
    print("Server is running without any environment ⛔")
else:
    print(f"Server is running in {environment} environment 🚀")


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
