import os
from pymongo import MongoClient
from utils.constants import Environment


db = None


def connect():
    flask_env = os.environ.get("FLASK_ENV")
    if flask_env == Environment.DEVELOPMENT.value:
        mongodb_uri = os.environ.get("DB_CONNECTION_URI_LOCAL")
    else:
        mongodb_uri = os.environ.get("DB_CONNECTION_URI")
        mongodb_uri = mongodb_uri.replace("{USERNAME}", os.environ.get(
            "DB_USERNAME")).replace("{PASSWORD}", os.environ.get("DB_PASSWORD"))

    client = MongoClient(mongodb_uri)
    global db
    db = client.get_database(os.environ.get("DB_NAME"))

    if db is None:
        print("failed connected to the database ❌")
    else:
        print("connected to the database 🚀")


def get_db():
    if db is None:
        raise Exception("failed to start the database")
    return db

# 1) connect laptop and mobile to the same wifi network
# 2) developer option -> usb debugging (open)
# 3) connect the mobile phone with the laptop using usb cabel
# 4) run this command in the vs code terminal `python api/app.py`
# 5) run the app from the android studio


# database => for storing the data like user's data, product's data etc. => mongodb

# client app => UI => kotlin

# server => api => connecting the database and client app => python