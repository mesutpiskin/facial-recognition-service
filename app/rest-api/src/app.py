from flask import Flask, json, Response, request, render_template
from werkzeug.utils import secure_filename
from os import path, getcwd
import time
from face import Face
import glob
import yaml
import os
import sys
import pickle
from flasgger import swag_from, Swagger
import base64
import uuid
from PIL import Image
from io import BytesIO

# INIT
app = Flask(__name__)
app.config['file_allowed'] = ['image/png', 'image/jpeg']
app.config['storage'] = path.join(getcwd(), './storage')
app.face = Face(app)
app.config['SWAGGER'] = {
    'title': 'Face API',
    'uiversion': 3
}
swagger = Swagger(app)

# HTTP RESULTS

def http_success_result(success_message, data, status=200, mimetype='application/json'):
    return Response(json.dumps({"result": {"message": success_message, "data": data}}), status=status, mimetype=mimetype)

def http_error_result(error_message, error_code, status=500, mimetype='application/json'):
    return Response(json.dumps({"result": {"message": error_message, "code": error_code}}), status=status, mimetype=mimetype)

# ---------------------------


# Add new person and train dataset
@app.route('/api/newface', methods=['POST'])
@swag_from(yaml.load(open("../swagger/newface.yml")))
def upload_face_and_train():
    content = request.json

    if not content['image']:
        return http_error_result("Image is required.", "1005")
    else:     
        base64_image = content['image']
        unic_filename = str(uuid.uuid4())+ ".jpg"
        file_path = '../storage/temp/' + unic_filename
        im = Image.open(BytesIO(base64.b64decode(base64_image)))
        im.save(file_path, 'JPEG')

        # call search face in image
        face_result = app.face.search_face_in_image(file_path)
        if face_result:
            os.remove(file_path)
            return http_error_result(face_result+ "", "1011")

        # get name in form data
        name =  content['id']


        base64_image = content['image']
        filename = name+ ".jpg"
        file_path = '../storage/trained/' + filename
        im = Image.open(BytesIO(base64.b64decode(base64_image)))
        im.save(file_path, 'JPEG')


        # start train
        app.face.train_dataset()

        #return_output = json.dumps({"id": user_id, "name": name, "face": [face_data]})
        return http_success_result("Photo was uploaded and the dataset was re train.", None)

# Train face dataset
@app.route('/api/train', methods=['POST'])
def train():
    app.face.train_dataset()
    #return_output = json.dumps({"id": user_id, "name": name, "face": [face_data]})
    return http_success_result("Dataset was re train.")

# Router for recognize a unknown face
@app.route('/api/recognize', methods=['POST'])
def recognize():
    content = request.json

    if not content['image']:
        return http_error_result("Image is required.", "1005")
    else:
        base64_image = content['image']

        unic_filename = str(uuid.uuid4())+ ".jpg"
        file_path = '../storage/temp/' + unic_filename
        im = Image.open(BytesIO(base64.b64decode(base64_image)))
        im.save(file_path, 'JPEG')

        result = app.face.recognize(file_path)
        os.remove(file_path)


        return http_success_result("", result)

# Clear face data and image storage folder
@app.route('/api/delete', methods=['POST'])
def clear_face():

    files = glob.glob('../storage/trained/*')
    for f in files:
        os.remove(f)
    
    files = glob.glob('../storage/temp/*')
    for f in files:
        os.remove(f)

    app.face.train_dataset()

    return http_success_result("All faces is deleted.", "")

# Get registired face list
@app.route('/api/ids', methods=['GET'])
def get_face_list():
    face_list = []
    with open('../storage/db/face.data', 'rb') as filehandle:  
        face_list = pickle.load(filehandle)

    if not face_list:
       return http_error_result("No face registired.","1004")

    #makeitastring = '<br/>'.join(map(str, face_list))   
    return http_success_result("Registired faces.", face_list)


# Get detected face locations
@app.route('/api/detect', methods=['POST'])
def face_detect():
    content = request.json

    if not  content['image']:
        return http_error_result("Image is required.", "1005")
    else:
        base64_image = content['image']

        unic_filename = str(uuid.uuid4())+ ".jpg"
        file_path = '../storage/temp/' + unic_filename
        im = Image.open(BytesIO(base64.b64decode(base64_image)))
        im.save(file_path, 'JPEG')

        locations = app.face.detect_faces_in_image(file_path)

        os.remove(file_path)
        
        return http_success_result("Detected face locations.", locations)









# ==============| RUN APP |==============
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port="8080")




