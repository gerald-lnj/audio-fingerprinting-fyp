""" controller and routes for users """
import os
from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity,
)
from app import app, mongo, flask_bcrypt, jwt
from app.schemas import user_schema
from validx import exc
import traceback

# import logger

ROOT_PATH = os.environ.get("ROOT_PATH")
# LOG = logger.get_root_logger(
#     __name__, filename=os.path.join(ROOT_PATH, 'output.log'))


@jwt.unauthorized_loader
def unauthorized_response(callback):
    return jsonify({"ok": False, "message": "Unauthorised"}), 401


@app.route("/auth", methods=["POST"])
def auth_user():
    """ auth endpoint """
    form_data = request.form

    try:
        user_schema(form_data)
    except exc.ValidationError as e:
        return jsonify({"ok": False, "message": "Bad request parameters"}), 400
    else:
        user = mongo.db.users.find_one(
            {"email": form_data["email"]},
            {"_id": 0},  # this line removes the _id key from the returned obj
        )
        if user and flask_bcrypt.check_password_hash(
            user["password"], form_data["password"]
        ):
            del user["password"]
            access_token = create_access_token(identity=form_data)
            refresh_token = create_refresh_token(identity=form_data)
            user["token"] = access_token
            user["refresh"] = refresh_token
            return jsonify({"ok": True, "data": user}), 200
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
    except exc.ValidationError as e:

        return jsonify({"ok": False, "message": "Bad request parameters: "}), 400
    else:
        try:
            user = mongo.db.users.find_one({"email": form_data["email"]}, {"_id": 0})

            if user == None:
                mongo.db.users.insert_one({
                    'name': form_data['name'],
                    'email': form_data['email'],
                    'password': flask_bcrypt.generate_password_hash(form_data["password"]).decode("utf-8")
                })
                return jsonify({"ok": True, "message": "User created successfully!"}), 200
            else:
                return (
                    jsonify(
                        {"ok": False, "message": "User with this email already exists!"}
                    ),
                    409,
                )
        except Exception as e:
            print(traceback.format_exc())
            return (
                jsonify(
                    {"ok": False, "message": "Unexpected error occured!"}
                ), 500
            )


@app.route("/refresh", methods=["POST"])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    ret = {
        'access_token': create_access_token(identity=current_user)
    }
    return jsonify(ret), 200


@app.route("/user", methods=["GET", "DELETE", "PATCH"])
@jwt_required
def user():
    """ route read user """
    email = get_jwt_identity()["email"]

    if request.method == "GET":
        data = mongo.db.users.find_one({"email": email}, {"_id": 0})
        return jsonify({"ok": True, "data": data}), 200

    if request.method == "DELETE":
        db_response = mongo.db.users.delete_one({"email": email})
        if db_response.deleted_count == 1:
            response = {"ok": True, "message": "record deleted"}
        else:
            response = {"ok": True, "message": "no record found"}
        return jsonify(response), 200

    data = request.get_json()

    if request.method == "PATCH":
        if data.get("query", {}) != {}:
            mongo.db.users.update_one(data["query"], {"$set": data.get("payload", {})})
            return jsonify({"ok": True, "message": "record updated"}), 200
        else:
            return jsonify({"ok": False, "message": "Bad request parameters!"}), 400
