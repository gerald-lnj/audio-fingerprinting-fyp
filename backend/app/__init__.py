from flask import Flask
from flask_cors import CORS
import os
import json
import datetime
from bson.objectid import ObjectId
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

load_dotenv()


class JSONEncoder(json.JSONEncoder):
    # extend json-encoder class to support ObjectId & datetime data types
    # used to store ‘_id’ & ‘time-stamp’ respectively in MongoDB, convert to strings

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, set):
            return list(o)
        if isinstance(o, datetime.datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)


app = Flask(__name__)

# configuration
DEBUG = True

# add mongo url to flask config, so that flask_pymongo can use it to make connection
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(days=1)
DEBUG = os.getenv("DEBUG")


mongo = PyMongo(app)

# init stuff
flask_bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# use the modified encoder class to handle ObjectId & datetime object while jsonifying the response.
app.json_encoder = JSONEncoder

# enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})

from app import routes
from app.controllers import *
