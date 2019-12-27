from flask import jsonify
from app import app

# sanity check route

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"


@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')
