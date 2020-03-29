""" controller and routes for users """
import os
import traceback
from bson.objectid import ObjectId
from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity,
)
from validx import exc
from app import app, mongo, flask_bcrypt, jwt
from app.schemas import user_schema, delete_vid_schema
from pymongo import DeleteOne
from pymongo.errors import BulkWriteError

# import logger

ROOT_PATH = os.environ.get("ROOT_PATH")
# LOG = logger.get_root_logger(
#     __name__, filename=os.path.join(ROOT_PATH, 'output.log'))

USERS_COLLECTION = mongo.db.users  # holds reference to videos
VIDEOS_COLLECTION = mongo.db.videos  # holds reference to links
LINKS_COLLECTION = mongo.db.links  # holds reference to fingerprints
FINGERPRINTS_COLLECTION = mongo.db.fingerprints  # holds reference to links (in couples)


@jwt.unauthorized_loader
def unauthorized_response(callback):
    return jsonify({"ok": False, "message": "Unauthorised"}), 401


@app.route("/auth", methods=["POST"])
def auth_user():
    """ auth endpoint """
    form_data = request.form

    try:
        user_schema(form_data)
    except exc.ValidationError:
        return jsonify({"ok": False, "message": "Bad request parameters"}), 400
    else:
        user_doc = USERS_COLLECTION.find_one(
            {"email": form_data["email"]},
            {"_id": 0},  # this line removes the _id key from the returned obj
        )
        if user_doc and flask_bcrypt.check_password_hash(
            user_doc["password"], form_data["password"]
        ):
            del user_doc["password"]
            del user_doc["videos"]
            access_token = create_access_token(identity=form_data)
            refresh_token = create_refresh_token(identity=form_data)
            user_doc["token"] = access_token
            user_doc["refresh"] = refresh_token
            return jsonify({"ok": True, "data": user_doc}), 200
        else:
            return (
                jsonify({"ok": False, "message": "invalid username or password"}),
                401,
            )


@app.route("/register", methods=["POST"])
def register():
    """
    register user endpoint
    expects form data in the format:
    "name": string,
    "email": email string,
    "password": string, len>8,

    more details in user_schema
    """
    form_data = request.form

    try:
        # data = request.get_json(force=True)
        # user_schema(request.get_json(force=True))
        user_schema(form_data)
    except exc.ValidationError:
        return jsonify({"ok": False, "message": "Bad request parameters: "}), 400
    else:
        try:
            user_doc = USERS_COLLECTION.find_one(
                {"email": form_data["email"]}, {"_id": 0}
            )

            if user_doc is None:
                USERS_COLLECTION.insert_one(
                    {
                        "name": form_data["name"],
                        "email": form_data["email"],
                        "password": flask_bcrypt.generate_password_hash(
                            form_data["password"]
                        ).decode("utf-8"),
                        "videos": [],
                    }
                )
                return (
                    jsonify({"ok": True, "message": "User created successfully!"}),
                    200,
                )
            else:
                return (
                    jsonify(
                        {"ok": False, "message": "User with this email already exists!"}
                    ),
                    409,
                )
        except Exception:
            print(traceback.format_exc())
            return (jsonify({"ok": False, "message": "Unexpected error occured!"}), 500)


@app.route("/refresh", methods=["POST"])
@jwt_refresh_token_required
def refresh():
    """
    When JWT has expired, issue new one with refresh token
    """
    current_user = get_jwt_identity()
    ret = {"access_token": create_access_token(identity=current_user)}
    return jsonify(ret), 200


@app.route("/user", methods=["GET", "DELETE", "PATCH"])
@jwt_required
def user():
    """ route read user """
    email = get_jwt_identity()["email"]

    if request.method == "GET":
        user_doc = USERS_COLLECTION.find_one({"email": email}, {"_id": 0})

        try:
            video_ids = user_doc["videos"]
        except TypeError:
            return 404
        result = list_videos(video_ids)
        return jsonify({"ok": True, "data": result}), 200

    if request.method == "DELETE":
        user_doc = USERS_COLLECTION.find_one({"email": email}, {"_id": 0})

        if user_doc is None:
            return 404

        for video_id in user_doc["videos"]:
            delete_video(video_id)

        db_response = USERS_COLLECTION.delete_one({"email": email})
        if db_response.deleted_count == 1:
            response = {"ok": True, "message": "record deleted"}
        else:
            response = {"ok": True, "message": "no record found"}
        return jsonify(response), 200

    data = request.get_json()

    if request.method == "PATCH":
        if data.get("query", {}) != {}:
            USERS_COLLECTION.update_one(
                data["query"], {"$set": data.get("payload", {})}
            )
            return jsonify({"ok": True, "message": "record updated"}), 200
        return jsonify({"ok": False, "message": "Bad request parameters!"}), 400


def purge_records(email):
    data = USERS_COLLECTION.find_one({"email": email}, {"_id": 0})


def list_videos(video_ids):
    result = []
    for video_id in video_ids:

        video = VIDEOS_COLLECTION.find_one({"_id": video_id})
        links = []
        for link_id in video["links"]:
            link = LINKS_COLLECTION.find_one({"_id": link_id})
            link["_id"] = str(link["_id"])
            del link["fingerprints"]
            links.append(link)
        # result[video['name']] = links
        temp_result = {
            "_id": video_id,
            "name": video["name"],
            "links": links,
            "mode": video["mode"],
        }
        result.append(temp_result)
    return result


@app.route("/delete-video", methods=["POST"])
@jwt_required
def delete_video(video_id=None):
    if video_id is None:
        form_data = request.form
        try:
            delete_vid_schema(form_data)
        except exc.ValidationError as e:
            print(e)

            return jsonify({"ok": False, "message": "Bad request parameters"}), 400
        video_id = ObjectId(form_data["video_id"])
    try:
        email = get_jwt_identity()["email"]
        user_doc = USERS_COLLECTION.find_one({"email": email}, {"_id": 0})

        video_doc = VIDEOS_COLLECTION.find_one({"_id": video_id})

        if video_doc is not None:
            if video_doc["upllader_email"] != email:
                return 401
            # build internal store of links in video
            us_docs = []
            us_ids = video_doc["links"]

            if len(us_ids) > 0:
                for us_id in us_ids:
                    us_docs.append(LINKS_COLLECTION.find_one({"_id": us_id}))

                # build internal store of fingeprints in each link
                fp_docs = {}
                for us_doc in us_docs:
                    fp_ids = us_doc["fingerprints"]
                    for fp_id in fp_ids:
                        if fp_id not in fp_docs:
                            fp_docs[fp_id] = FINGERPRINTS_COLLECTION.find_one(
                                {"_id": fp_id}
                            )

                # delete relevant couples from fingerprint
                for fp_id, fp_doc in fp_docs.items():
                    new_couples = [
                        couple
                        for couple in fp_doc["couple"]
                        if couple["link_id"] not in us_ids
                    ]

                    # if there are unrelated couples, overwrite the 'couple' field with new_couples
                    if len(new_couples) > 0:
                        FINGERPRINTS_COLLECTION.update_one(
                            {"_id": fp_id}, {"$set": {"couple": new_couples}}
                        )
                    # else, delete the fingerprint
                    else:
                        FINGERPRINTS_COLLECTION.delete_one({"_id": fp_id})

                # delete all links
                requests = [DeleteOne({"_id": us_id}) for us_id in us_ids]
                LINKS_COLLECTION.bulk_write(requests)

            # delete video
            VIDEOS_COLLECTION.delete_one({"_id": video_doc["_id"]})

            USERS_COLLECTION.update_one(
                {"email": email}, {"$pull": {"videos": video_doc["_id"]}}
            )

            return (
                jsonify({"ok": True, "message": "Success!",}),
                200,
            )
        else:
            return jsonify({"ok": False, "message": "The file was not found"}), 404
    except Exception as e:
        print(e)
        return jsonify({"ok": False, "message": "There was an error"}), 500
