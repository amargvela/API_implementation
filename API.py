#!flask/bin/python
import os.path
import json
import uuid

from flask import Flask, jsonify, abort
from flask import request, url_for, Response

filename = os.environ['API_OBJECTS']
app = Flask(__name__)


# Reads file containing objects as a list of dictionaries.
# If file doesn't exist or exists but doesn't have
# json format, reinitializes it.
def read_file(filename):
    try:
        with open(filename, 'r') as f:
            content = json.load(f)
        return content
    except (OSError, IOError, ValueError):
        with open(filename, 'w') as f:
            f.write(json.dumps([], indent=4))
    with open(filename, 'r') as f:
        return json.load(f)


# Creates an arror dictionary based on given values
def error_message(verb, url, text):
    message = {}
    message['verb'] = verb
    message['url'] = url
    message['message'] = text
    return jsonify(message)


# Implements POST - adds object in the list
@app.route('/api/objects', methods=['POST'])
def create_object():
    objects = read_file(filename)
    url = url_for('create_object', _external = True)
    try:
        new_object = json.loads(request.data)
    except ValueError:
        return error_message('POST', url, 'Not a JSON object')
    if not isinstance(new_object, dict):
        return error_message('POST', url, 'Not a JSON object')
    if 'uid' in request.json:
        return error_message('POST', url, "'uid' is already used as a key")
    new_object['uid'] = str(uuid.uuid4())
    objects.append(new_object)
    with open(filename, 'w') as f:
        f.write(json.dumps(objects, indent=4))
    return jsonify(new_object)


# Implements PUT - updates object in the list
@app.route('/api/objects/<string:object_id>', methods=['PUT'])
def update_object(object_id):
    objects = read_file(filename)
    contains_id = False
    for curr_object in objects:
        if curr_object['uid'] == object_id:
            contains_id = True
            objects.remove(curr_object)
            break
    url = url_for('update_object', object_id=object_id, _external = True)
    if contains_id == False:
        return error_message('PUT', url, "Given ID doesn't exist")
    try:
        new_object = json.loads(request.data)
    except ValueError:
        return error_message('PUT', url, 'Not a JSON object')
    if not isinstance(new_object, dict):
        return error_message('PUT', url, 'Not a JSON object')
    new_object['uid'] = object_id
    objects.append(new_object)
    with open(filename, 'w') as f:
        f.write(json.dumps(objects, indent=4))
    return jsonify(new_object)


# Implements GET - returns the entire list
@app.route('/api/objects', methods=['GET'])
def get_objects():
    objects = read_file(filename)
    return json.dumps(objects, indent=4)


# Implements GET - returns an object with the given ID.
# If ID doesn't exist returns error message
@app.route('/api/objects/<string:object_id>', methods=['GET'])
def get_object(object_id):
    objects = read_file(filename)
    for curr_obj in objects:
        if curr_obj['uid'] == object_id:
            return jsonify(curr_obj)
    url = url_for('get_object', object_id=object_id, _external = True)
    return error_message('GET', url, "Given ID doesn't exist")


# Implements DELETE - removes an object with the given ID from the list.
# If ID doesn't exist does nothing
# Returns empty dictionary that should be ignored.
@app.route('/api/objects/<string:object_id>', methods=['DELETE'])
def delete_object(object_id):
    objects = read_file(filename)
    passed_object = None
    for curr_object in objects:
        if curr_object['uid'] == object_id:
            passed_object = curr_object
            break
    if passed_object != None:
        objects.remove(passed_object)
    with open(filename, 'w') as f:
        f.write(json.dumps(objects, indent=4))
    return jsonify({})


# Makes sure script is run when program is called directly from python
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

