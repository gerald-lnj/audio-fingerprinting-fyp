""" flask app with mongo """
import os
import json
import datetime
from apscheduler.jobstores.mongodb import MongoDBJobStore
from bson.objectid import ObjectId
from flask import Flask
from flask_apscheduler import APScheduler
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv(".flaskenv")

# create the flask object
app = Flask(__name__)


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


app.json_encoder = JSONEncoder

# CORS stuff
CORS(app)

# Bcrypt stuff
flask_bcrypt = Bcrypt(app)

# config mongo uri
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)

# config JWT stuff
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)

# config uploader stuff
app.config["UPLOADED_VIDEOS_DEST"] = os.getenv("UPLOADED_VIDEOS_DEST")

# config apscheduler stuff
app.config["SCHEDULER_API_ENABLED"] = True
app.config["SCHEDULER_JOBSTORES"] = {
    "default": MongoDBJobStore(
        database="fyp", collection="jobs", host="localhost", port=27017
    )
}

# def checkCollections():
#     required_collections = [
#         'ultrasound_fingerprints',
#         'jobs',
#         'audible_fingerprints',
#         'users',
#         'videos',
#         'links'
#     ]
#     existing_collections = mongo.db.list_collection_names()
#     for collection in required_collections:
#         if collection not in existing_collections:
#             mongo.db.create_collection(collection)
# 
# checkCollections()

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

from app.routes import *
