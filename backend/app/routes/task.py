"""
routes for tasks
"""

from datetime import datetime, timedelta
import os
from flask import request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
from flask_uploads import UploadSet, configure_uploads, UploadNotAllowed
from validx import exc
from scipy.io import wavfile
from app import app, mongo, scheduler
from app.schemas import upload_schema
from ..controllers import (
    audio_analysis,
    audio_hashing,
    audio_matching,
    create_audio,
    audio_overlay,
)


VIDEOS = UploadSet(name="videos", extensions=("mp4"))
configure_uploads(app, VIDEOS)
CWD = os.getcwd()

USERS_COLLECTION = mongo.db.users # holds reference to videos
VIDEOS_COLLECTION = mongo.db.videos  # holds reference to links
LINKS_COLLECTION = mongo.db.links  # holds reference to fingerprints
FINGERPRINTS_COLLECTION = (
    mongo.db.fingerprints
)  # holds reference to links (in couples)


@app.route("/upload", methods=["POST"])
@jwt_required
def upload_file():
    """
    function that handles uploading files
    """

    # data received: file, timestamps with links, userid
    video = request.files.get("file")
    form_data = request.form
    try:
        upload_schema(form_data)
    except exc.ValidationError:
        return jsonify({"ok": False, "message": "Bad request parameters"}), 400

    email = get_jwt_identity()['email']
    mode = form_data['mode']
    filename = request.files["file"].filename.split(".")[0]

    # save file
    time = (
        datetime.now()
        .isoformat(sep="T", timespec="seconds")
        .replace("T", "")
        .replace(":", "")
        .replace("-", "")
    )
    try:
        video_filename = VIDEOS.save(video, name="{}-{}.".format(filename, time))
    except UploadNotAllowed:
        return jsonify({"ok": False, "message": "The file was not allowed"}), 400

    # record video and uploader to db
    video_document = {
        "name": video_filename,
        "uploader_email": email,
        "links": [],
        "mode": mode
    }
    video_id = VIDEOS_COLLECTION.insert_one(video_document).inserted_id

    # format formdata links for processing
    time_dicts = [
        {
            "start": int(time_entry.split("::")[0]),
            "end": int(time_entry.split("::")[1]),
            "link": time_entry.split("::")[2],
        }
        for time_entry in form_data.getlist("time")
    ]
    time_dicts = sorted(time_dicts, key=lambda k: k["start"])

    # for each link
    for i, _p in enumerate(time_dicts):
        # use link as seed to generate 10s wav file,
        seed = "{}{}{}{}".format(_p["start"], _p["end"], _p["link"], video_id)

        if mode == 'ultrasound':
            # generate ultrasound
            audio_filename = create_audio.ultrasound_generator(seed)
        else:
            audio_filename = create_audio.audio_extractor(video_filename, seed, _p['start'], _p['end'])
        time_dicts[i]["filepath"] = "{}/output_audio/{}.wav".format(
            CWD, audio_filename
        )

        # record link to db
        link_document = {
            "type": "link",
            "content": _p["link"],
            "start": _p["start"],
            "end": _p["end"],
            "fingerprints": []
        }
        link_id = LINKS_COLLECTION.insert_one(
            link_document
        ).inserted_id

        # add the link ObjectID to time_dicts for saving to video collection
        time_dicts[i]["_id"] = link_id

        link_audio_fingerprints = {}

        # analyse audio wav file and generate peaks and fingeprints
        _, data = wavfile.read(
            "{}/output_audio/{}.wav".format(CWD, audio_filename)
        )
        peaks = audio_analysis.analyse(data, mode)

        fingerprints = audio_hashing.hasher(peaks, link_id)

        # collate address and couples
        for fingerprint in fingerprints:
            address = fingerprint["address"]
            couple = fingerprint["couple"]

            if address not in link_audio_fingerprints:
                # if fingerprint address is not in collection, insert new document
                link_audio_fingerprints[address] = [couple]

            else:
                # if fingerprint address already exists, append couple
                # TODO: is there a way to check if couple list already includes couple?
                link_audio_fingerprints[address].append(couple)
        fingerprints_ids = []
        for address, couple_list in link_audio_fingerprints.items():
            fingerprint_id = FINGERPRINTS_COLLECTION.find_one({'address': address})
            if fingerprint_id:
                _id = FINGERPRINTS_COLLECTION.update_one(
                    {'address': address}, {
                        "$push": {
                            "couple": {"$each": couple_list}
                        }
                    }
                ).upserted_id
            else:
                _id = FINGERPRINTS_COLLECTION.insert_one(
                    {'address': address, "couple": couple_list}
                ).inserted_id
            fingerprints_ids.append(_id)
        LINKS_COLLECTION.update_one(
            {'_id': link_id},
            {
                "$push": {
                    "fingerprints": {"$each": fingerprints_ids}
                }
            }
        )

    USERS_COLLECTION.update_one(
        {'email': email},
        {
            "$push":
            {
                "videos": ObjectId(video_id)
            }
        }
    )

    # 4: generate new video
    video_filepath = "{}/uploaded_files/{}".format(CWD, video_filename)
    output_video_filepath = audio_overlay.main(video_filepath, time_dicts)
    
    VIDEOS_COLLECTION.update_one(
        {'_id': video_id},
        {
            "$push":
            {
                "links": {"$each": [i["_id"] for i in time_dicts]}
            },
            "$set": {"uploaded_video": video_filename}
        }
    )

    # 5: cleanup
    for i, _ in enumerate(time_dicts):
        os.remove(time_dicts[i]["filepath"])
    os.remove("{}/uploaded_files/{}".format(CWD, video_filename))


    run_time = datetime.now() + timedelta(hours=2)
    scheduler.add_job(
        id=str(video_id),
        func=delete_video_delayed,
        args=[output_video_filepath],
        trigger='date',
        run_date=run_time,
        misfire_grace_time=2592000
    )

    return jsonify({"ok": True, "message": video_filename}), 200

def delete_video_delayed(filepath):
    """
    Function that removes the file at filepath. 
    Called by apcheduler
    """
    try:
        os.remove(filepath)
    except FileNotFoundError:
        pass
    print('file {} deleted!'.format(filepath.split('/')[-1]))

@app.route("/get-video/<string:video_name>", methods=["GET"])
def download(video_name):
    """func to dynamically retrieve video files"""
    try:
        return send_from_directory(
            "{}/output_video".format(CWD), filename=video_name, as_attachment=True
        )
    except FileNotFoundError:
        return jsonify({"ok": False, "message": "The file was not found"}), 404

@app.route("/detect", methods=["POST"])
def detect():
    """function that calls the matching func"""
    # match_audio = request.files.get("file")
    # form_data = request.form

    # read file from req
    if 'audio' not in request.files.keys():
        return (
            jsonify(
                {"ok": False, "message": "Expected WAV file missing"}
            ),
            415,
        )

    audio_file = request.files.get('audio')
    _, data = wavfile.read(audio_file)

    # get peaks
    peaks = audio_analysis.analyse(data)
    # generate fingerprints
    fingerprints = audio_hashing.hasher(peaks)

    # match on fingerprints
    object_id, match_max = audio_matching.match(fingerprints)

    if object_id is None:
        print('Nothing detected')
        return (
            jsonify({"ok": True, "message": "No matches found"}),
            204,
        )
    else:
        link_audio_id = LINKS_COLLECTION.find_one({"_id": object_id})
        print('\nObjectID: {}'.format(object_id))
        print('Contents: {}'.format(link_audio_id["content"]))
        print('Match_max: {}'.format(match_max))
        return (
            jsonify(
                {
                    "ok": True,
                    "message": link_audio_id["content"],
                }
            ),
            200,
        )


@app.route("/debug", methods=["POST"])
@jwt_required
def debug():
    """ endpoint for me to test quick stuff"""
    return (
        jsonify(
            {
                "ok": True,
                "message": 'testing',
            }
        ),
        200,
    )


@app.route("/purge")
def purge():
    """
    purge all documents in all collections except users
    clears records of videos from users
    """
    VIDEOS_COLLECTION.remove({})
    LINKS_COLLECTION.remove({})
    FINGERPRINTS_COLLECTION.remove({})
    USERS_COLLECTION.update({}, {"$set": {"videos": []}}, multi=True)
    return "purged records"
