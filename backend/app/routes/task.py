'''
routes for tasks
'''

from flask import request, jsonify, send_from_directory, after_this_request
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
from app import app, mongo
from app.schemas import upload_schema
from werkzeug import secure_filename
from flask_uploads import (UploadSet, configure_uploads, UploadNotAllowed)
from validx import exc
import base64
from scipy.io import wavfile
from ..controllers import audio_analysis, audio_hashing, create_ultrasound, audio_overlay
import os
import ffmpeg
# import ..controllers import as A



VIDEOS = UploadSet(name='videos', extensions=('mp4'))
configure_uploads(app, VIDEOS)
CWD = os.getcwd()

''' examples
@app.route('/task', methods=['GET', 'POST', 'DELETE', 'PATCH'])
# @jwt_required
def task():
    route read tasks
    if request.method == 'GET':
        query = request.args
        data = mongo.db.tasks.find_one({'_id': ObjectId(query['id'])})
        return jsonify({'ok': True, 'data': data}), 200

    data = request.get_json()

    if request.method == 'POST':
        user = get_jwt_identity()
        data['email'] = user['email']
        data = validate_task(data)
        if data['ok']:
            db_response = mongo.db.tasks.insert_one(data['data'])
            return_data = mongo.db.tasks.find_one(
                {'_id': db_response.inserted_id})
            return jsonify({'ok': True, 'data': return_data}), 200
        else:
            return jsonify({'ok': False, 'message': 'Bad request parameters: {}'.format(data['message'])}), 400

    if request.method == 'DELETE':
        if data.get('id', None) is not None:
            db_response = mongo.db.tasks.delete_one(
                {'_id': ObjectId(data['id'])})
            if db_response.deleted_count == 1:
                response = {'ok': True, 'message': 'record deleted'}
            else:
                response = {'ok': True, 'message': 'no record found'}
            return jsonify(response), 200
        else:
            return jsonify({'ok': False, 'message': 'Bad request parameters!'}), 400

    if request.method == 'PATCH':
        data = validate_task_update(data)
        if data['ok']:
            data = data['data']
            mongo.db.tasks.update_one(
                {'_id': ObjectId(data['id'])}, {'$set': data['payload']})
            return jsonify({'ok': True, 'message': 'record updated'}), 200
        else:
            return jsonify({'ok': False, 'message': 'Bad request parameters: {}'.format(data['message'])}), 400

@app.route('/list/task', methods=['GET'])
@jwt_required
def list_tasks():
    route to get all the tasks for a user
    user = get_jwt_identity()
    if request.method == 'GET':
        query = request.args
        data = mongo.db.tasks.find({'email': user['email']})
        if query.get('group', None):
            return_data = {}
            for task in data:
                try:
                    return_data[task['status']].append(task)
                except:
                    return_data[task['status']] = [task]
        else:
            return_data = list(data)
        return jsonify({'ok': True, 'data': return_data})
'''

@app.route('/upload', methods=['POST'])
@jwt_required
def upload_file():
    ''' pseudocode
    1: data received: video, timestamps with links, userid

    2: save video and record in db
    3: for each link:
      3a: use link as seed to generate 10s wav file, add document to ultrasound collection
      3b: analyse wav file and generate peaks
      3c: hash each fingerprint and add to database
    4: generate new video
    5: cleanup
    '''
    users_collection = mongo.db.users
    videos_collection = mongo.db.videos # holds reference to user
    ultrasound_collection = mongo.db.ultrasound # holds reference to video
    fingerprints_collection = mongo.db.fingerprints # holds reference to ultrasound (in couples)

    # 1: data received: file, timestamps with links, userid
    video = request.files.get('file')
    form_data = request.form
    try:
        upload_schema(form_data)
    except exc.ValidationError:
        return jsonify({'ok': False, 'message': 'Bad request parameters'}), 400
    else:
        email = form_data['email']
        filename = request.files['file'].filename.split('.')[0]
        #2a: save file
        try:
            video_filename = VIDEOS.save(video, name='{}-{}.'.format(filename, email))
        except UploadNotAllowed:
            return jsonify({'ok': False, 'message': 'The file was not allowed'}), 400
        else:
            # 2b: and record in db
            video_document = {
                'name': video_filename,
                'uploader_email': email,
            }
            video_id = videos_collection.insert_one(video_document).inserted_id

            # 3: for each link:
            time_dicts = [
                {
                    'start': int(time_entry.split('::')[0]),
                    'end': int(time_entry.split('::')[1]),
                    'link': time_entry.split('::')[2],
                } for time_entry in form_data.getlist('time')
            ]
            time_dicts = sorted(time_dicts, key=lambda k: k['start'])

            # 3ai: generate ultrasound and fingerprints and add to db
            for i, _p in enumerate(time_dicts):
                # 3aii: use link as seed to generate 10s wav file, add document to ultrasound collection
                ultrasound_filename = create_ultrasound.noise_generator(_p['link'])
                time_dicts[i]['filepath'] = '{}/output_audio/{}.wav'.format(CWD, ultrasound_filename)

                ultrasound_document = {
                    'type': 'link',
                    'content': _p['link'],
                    'start': _p['start'],
                    'end': _p['end'],
                    'video_id': ObjectId(video_id)
                }
                ultrasound_id = ultrasound_collection.insert_one(ultrasound_document).inserted_id

                # 3aiii: analyse wav file and generate peaks
                _, data = wavfile.read('{}/output_audio/{}.wav'.format(CWD, ultrasound_filename))
                peaks = audio_analysis.analyse(data)

                # 3aiv: hash each fingerprint and add to database
                fingerprints = audio_hashing.hasher(peaks, ultrasound_id)

                for fingerprint in fingerprints:
                    address = fingerprint['address']
                    couple = fingerprint['couple']

                    if fingerprints_collection.find_one({'address': address}) is None:
                        # if fingerprint address is not in collection, insert new document
                        fingerprints_collection.insert_one({'address': address, 'couple': [couple]})

                    else:
                        # if fingerprint address already exists, append couple
                        fingerprints_collection.update_one({'address': address}, {'$push': {'couple': couple}})

            # 4: generate new video
            video_filepath = '{}/uploaded_files/{}'.format(CWD, video_filename)
            audio_overlay.main(video_filepath, time_dicts)

            # 5: cleanup
            for i, _ in enumerate(time_dicts):
                os.remove(time_dicts[i]['filepath'])
            os.remove('{}/uploaded_files/{}'.format(CWD, video_filename))

            return jsonify({'ok': True, 'message': 'File successfully uploaded!'}), 200

@app.route('/get-video/<string:video_name>', methods=['GET'])
@jwt_required
def download(video_name):
    user = get_jwt_identity()
    if user['email'] in video_name:
        try:
            # # delete file after download
            # @after_this_request
            # def remove_file(response):
            #     os.remove('{}/output_video/{}'.format(CWD, video_name))
            #     return response
            return send_from_directory('{}/output_video'.format(CWD), filename=video_name, as_attachment=True)
        except FileNotFoundError:
            return jsonify({'ok': False, 'message': 'The file was not found'}), 404
    else:
        return jsonify({'ok': False, 'message': 'You are not authorised to download this file'}), 404   
