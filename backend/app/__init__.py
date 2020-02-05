""" flask app with mongo """
import os
import json
import datetime
from bson.objectid import ObjectId
from flask import Flask
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt


from dotenv import load_dotenv

load_dotenv(".flaskenv")


class JSONEncoder(json.JSONEncoder):
    """ extend json-encoder class"""

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, set):
            return list(o)
        if isinstance(o, datetime.datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)


# create the flask object
app = Flask(__name__)

# config mongo uri
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

# config JWT stuff
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(days=1)

# config uploader stuff
app.config["UPLOADED_VIDEOS_DEST"] = os.getenv("UPLOADED_VIDEOS_DEST")

mongo = PyMongo(app)
flask_bcrypt = Bcrypt(app)
jwt = JWTManager(app)
app.json_encoder = JSONEncoder

from app.routes import *
