'''
routes for tasks
'''

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
from app import app, mongo
from app.schemas import upload_schema
from werkzeug import secure_filename
from flask_uploads import (UploadSet, configure_uploads, UploadNotAllowed)
from validx import exc
# import ..controllers import as A
from ..controllers import create_ultrasound



VIDEOS = UploadSet(name='videos', extensions=('mp4'))
configure_uploads(app, VIDEOS)

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
    1: data received: file, timestamps with links, userid
    2: save file
    2: for each link:
        a: use link as seed to generate 10s noise
        b: analyse and hash each ultrasound sequence
        c: save hash with link str to db
    3: add videoid to user's history, with audio hashes
    3: for each ultrasound:
        a: mix into original audio
    4: save new file, return
    5: delete old file
    '''
    video = request.files.get('file')
    form_data = request.form
    try:
        upload_schema(form_data)
    except exc.ValidationError:
        return jsonify({'ok': False, 'message': 'Bad request parameters'}), 400
    else:
        email = form_data['email']
        filename = request.files['file'].filename.split('.')[0]
        unique_filename = '{}-{}.'.format(filename, email)
        try:
            VIDEOS.save(video, name=unique_filename)
        except UploadNotAllowed:
            return jsonify({'ok': False, 'message': 'The file was not allowed'}), 400
        else:
            time_dicts = [
                {
                    'start': time_entry.split('::')[0],
                    'end': time_entry.split('::')[1],
                    'link': time_entry.split('::')[2],
                }
                for time_entry in form_data.getlist('time')
            ]
            # DEBUG
            print(time_dicts)
            for time_dict in time_dicts:
                create_ultrasound.noise_generator(time_dict['link'].replace('/', '_'))


            return jsonify({'ok': True, 'message': 'File successfully uploaded!'}), 200
