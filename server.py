from flask import Flask, request, jsonify
from routers.auth_routers import auth_blueprint
from routers.product_routers import product_blueprint
from routers.category_routers import category_bp
import traceback
import config
app = Flask(__name__)


app.register_blueprint(product_blueprint, url_prefix="/api/v1/products")
app.register_blueprint(auth_blueprint, url_prefix="/api/v1/auth")
app.register_blueprint(category_bp, url_prefix="/api/v1/categories")


@app.errorhandler(404)
def page_not_found(error):
    return jsonify({
        "status": "fail",
        "message": f"{request.path} is not found"
    }), 404


@app.errorhandler(405)
def method_not_found(error):
    return jsonify({
        "status": "fail",
        "message": f"{request.method} is not defined on {request.path}"
    }), 405


@app.errorhandler(Exception)
def handle_exception(error):
    print(traceback.format_exc())
    print(error)
    return jsonify({
        "status": "error",
        "message": "something went wrong"
    }), 500


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
