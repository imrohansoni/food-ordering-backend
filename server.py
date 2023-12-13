import os

from app import app

environment = os.environ.get("FLASK_ENV")
if environment == "development":
    print("server is running is development environment 🚀")
elif environment == "production":
    print("server is running in production environment 🚀")
else:
    print("server is running without any environment ⛔")

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True, load_dotenv=True)
