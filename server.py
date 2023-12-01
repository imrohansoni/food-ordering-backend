from flask import Flask, request
from routers.auth_routers import auth_blueprint
from routers.product_routers import product_blueprint


app = Flask(__name__)


app.register_blueprint(product_blueprint, url_prefix="/api/v1/products")
app.register_blueprint(auth_blueprint, url_prefix="/api/v1/auth")

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
