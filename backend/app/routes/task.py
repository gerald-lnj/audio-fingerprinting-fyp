"""
routes for tasks
"""

from datetime import datetime
import os
from flask import request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
from flask_uploads import UploadSet, configure_uploads, UploadNotAllowed
from validx import exc
from scipy.io import wavfile
from app import app, mongo
from app.schemas import upload_schema
from ..controllers import (
    audio_analysis,
    audio_hashing,
    audio_matching,
    create_ultrasound,
    audio_overlay,
)



VIDEOS = UploadSet(name="videos", extensions=("mp4"))
configure_uploads(app, VIDEOS)
CWD = os.getcwd()

USERS_COLLECTION = mongo.db.users
VIDEOS_COLLECTION = mongo.db.videos  # holds reference to user
ULTRASOUND_COLLECTION = mongo.db.ultrasound  # holds reference to video
FINGERPRINTS_COLLECTION = mongo.db.fingerprints # holds reference to ultrasound (in couples)


@app.route("/upload", methods=["POST"])
@jwt_required
def upload_file():
    """ pseudocode
    1: data received: video, timestamps with links, userid

    2: save video and record in db
    3: for each link:
      3a: use link as seed to generate 10s wav file, add document to ultrasound collection
      3b: analyse wav file and generate peaks
      3c: hash each fingerprint and add to database
    4: generate new video
    5: cleanup
    """

    # 1: data received: file, timestamps with links, userid
    video = request.files.get("file")
    form_data = request.form
    try:
        upload_schema(form_data)
    except exc.ValidationError:
        return jsonify({"ok": False, "message": "Bad request parameters"}), 400

    email = form_data["email"]
    filename = request.files["file"].filename.split(".")[0]
    # 2a: save file

    time = (
        datetime.now().isoformat(sep='T', timespec='seconds')
        .replace('T', '')
        .replace(':', '')
        .replace('-', '')
    )
    try:
        video_filename = VIDEOS.save(video, name="{}-{}.".format(filename, time))
    except UploadNotAllowed:
        return jsonify({"ok": False, "message": "The file was not allowed"}), 400

    # 2b: and record in db
    video_document = {
        "name": video_filename,
        "uploader_email": email,
    }
    video_id = VIDEOS_COLLECTION.insert_one(video_document).inserted_id

    # 3: for each link:
    time_dicts = [
        {
            "start": int(time_entry.split("::")[0]),
            "end": int(time_entry.split("::")[1]),
            "link": time_entry.split("::")[2],
        }
        for time_entry in form_data.getlist("time")
    ]
    time_dicts = sorted(time_dicts, key=lambda k: k["start"])

    # 3ai: generate ultrasound and fingerprints and add to db
    for i, _p in enumerate(time_dicts):
        # 3aii: use link as seed to generate 10s wav file,
        # add document to ultrasound collection
        seed = '{}{}{}{}'.format(_p["start"], _p["end"], _p["link"], video_id)
        ultrasound_filename = create_ultrasound.noise_generator(seed)
        time_dicts[i]["filepath"] = "{}/output_audio/{}.wav".format(
            CWD, ultrasound_filename
        )

        ultrasound_document = {
            "type": "link",
            "content": _p["link"],
            "start": _p["start"],
            "end": _p["end"],
            "video_id": ObjectId(video_id),
        }
        ultrasound_id = ULTRASOUND_COLLECTION.insert_one(
            ultrasound_document
        ).inserted_id

        # 3aiii: analyse wav file and generate peaks
        _, data = wavfile.read(
            "{}/output_audio/{}.wav".format(CWD, ultrasound_filename)
        )
        peaks = audio_analysis.analyse(data)

        # 3aiv: hash each fingerprint and add to database
        fingerprints = audio_hashing.hasher(peaks, ultrasound_id)

        for fingerprint in fingerprints:
            address = fingerprint["address"]
            couple = fingerprint["couple"]

            if FINGERPRINTS_COLLECTION.find_one({"address": address}) is None:
                # if fingerprint address is not in collection, insert new document
                FINGERPRINTS_COLLECTION.insert_one(
                    {"address": address, "couple": [couple]}
                )

            else:
                # if fingerprint address already exists, append couple
                # TODO: is there a way to check if couple list already includes couple?
                FINGERPRINTS_COLLECTION.update_one(
                    {"address": address}, {"$push": {"couple": couple}}
                )

    # 4: generate new video
    video_filepath = "{}/uploaded_files/{}".format(CWD, video_filename)
    audio_overlay.main(video_filepath, time_dicts)

    # 5: cleanup
    for i, _ in enumerate(time_dicts):
        os.remove(time_dicts[i]["filepath"])
    os.remove("{}/uploaded_files/{}".format(CWD, video_filename))

    return jsonify({"ok": True, "message": "File successfully uploaded!"}), 200


@app.route("/get-video/<string:video_name>", methods=["GET"])
@jwt_required
def download(video_name):
    '''func to dynamically retrieve video files'''
    user = get_jwt_identity()
    if user["email"] in video_name:
        try:
            # # delete file after download
            # @after_this_request
            # def remove_file(response):
            #     os.remove('{}/output_video/{}'.format(CWD, video_name))
            #     return response
            return send_from_directory(
                "{}/output_video".format(CWD), filename=video_name, as_attachment=True
            )
        except FileNotFoundError:
            return jsonify({"ok": False, "message": "The file was not found"}), 404
    else:
        return (
            jsonify(
                {"ok": False, "message": "You are not authorised to download this file"}
            ),
            404,
        )

@app.route("/match", methods=["POST"])
def match():
    '''function that calls the matching func'''
    # match_audio = request.files.get("file")
    # form_data = request.form
    # TODO: wav file validation


    # debug stuff

    # read wavfile
    _, data = wavfile.read("/Users/gerald/Documents/FYP/Bitcoin-20200205142533.wav")
 
    # get peaks
    peaks = audio_analysis.analyse(data)
    # generate fingerprints
    fingerprints = audio_hashing.hasher(peaks)

    # match on fingerprints
    object_id, match_max = audio_matching.match(fingerprints)

    if object_id is None:
        return (
            jsonify(
                {"ok": False, "message": "No matches found"}
            ),
            404,
        )
    else:
        ultrasound_id = ULTRASOUND_COLLECTION.find_one({'_id': object_id})
        video_id = VIDEOS_COLLECTION.find_one({'_id': ultrasound_id['video_id']})
        return jsonify(
            {
                "ok": True,
                "message": "Matched to {}".format(ultrasound_id['content'])
            }
            ), 200


@app.route("/debug", methods=["POST"])
def debug():
    ''' endpoint for me to test quick stuff'''
    return 'ok'

@app.route('/purge')
def purge():
    '''purge all documents in all collections except users'''
    VIDEOS_COLLECTION.remove({})
    ULTRASOUND_COLLECTION.remove({})
    FINGERPRINTS_COLLECTION.remove({})
    return 'ok'
