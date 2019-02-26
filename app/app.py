from flask import Flask, json, Response, request, render_template
from werkzeug.utils import secure_filename
from os import path, getcwd
import time
from face import Face
import glob
import os
import sys
import pickle

app = Flask(__name__)

app.config['file_allowed'] = ['image/png', 'image/jpeg']
app.config['storage'] = path.join(getcwd(), 'storage')
app.face = Face(app)


def success_handle(output, status=200, mimetype='application/json'):
    return Response(output, status=status, mimetype=mimetype)

def error_handle(error_message, status=500, mimetype='application/json'):
    return Response(json.dumps({"error": {"message": error_message}}), status=status, mimetype=mimetype)



#   Route for Hompage
@app.route('/', methods=['GET'])
def page_home():

    return render_template('index.html')

@app.route('/api', methods=['GET'])
def homepage():
    output = json.dumps({"api": '1.0'})
    return success_handle(output)


@app.route('/api/train', methods=['POST'])
def train():
    output = json.dumps({"success": True})

    if 'file' not in request.files:

        print ("Yüz içeren bir fotoğraf yüklemelisiniz.")
        return error_handle("Yüz içeren bir fotoğraf yüklemelisiniz.")
    else:

        print("File request", request.files)
        file = request.files['file']

        if file.mimetype not in app.config['file_allowed']:

            print("File extension is not allowed")
            return error_handle("Desteklenmeyen uzantı, yalnızca *.png ve *.jpg")
        else:

            # get name in form data
            name = request.form['name']

            print("Kayıt adı: ", name)

            print("Fotoğraf kaydedildi ", app.config['storage'])
            filename = secure_filename(file.filename)
            trained_storage = path.join(app.config['storage'], 'trained')
            file.save(path.join(trained_storage, filename))
            
            # rename file 2141xwawe1.png to mesut.png
            old_file = os.path.join(trained_storage, filename)
            photos_file_extension = filename.split(".")[-1]
            new_file_name = name+  "." + photos_file_extension
            new_file = os.path.join(trained_storage, new_file_name)
            os.rename(old_file, new_file)

            # start train
            app.face.train_dataset()

            #return_output = json.dumps({"id": user_id, "name": name, "face": [face_data]})
            return success_handle("Fotoğraf yüklendi ve dataset yeniden train edildi.")

# router for recognize a unknown face
@app.route('/api/recognize', methods=['POST'])
def recognize():
    if 'file' not in request.files:
        return error_handle("Lütfen fotoğraf seçiniz.")
    else:
        file = request.files['file']
        # file extension valiate
        if file.mimetype not in app.config['file_allowed']:
            return error_handle("Dosya uzantısı desteklenmiyor.")
        else:

            filename = secure_filename(file.filename)
            unknown_storage = path.join(app.config["storage"], 'unknown')
            file_path = path.join(unknown_storage, filename)
            file.save(file_path)

            customer_names = app.face.recognize(filename)
            #os.remove(file_path)

            if customer_names:
                #message = {"message": "Tespit sonucu: "+customer_names, "user": "customer_names"}
                return success_handle(customer_names)
            else:
                return error_handle("Kim olduğu tespit edilemedi.")

# clear sqlite and image storage folder
@app.route('/api/clear', methods=['POST'])
def clear_tables_and_datas():
   
    
    files = glob.glob('storage/trained/*')
    for f in files:
        os.remove(f)
    
    files = glob.glob('storage/unknown/*')
    for f in files:
        os.remove(f)

    app.face.train_dataset()

    return success_handle("Tüm kayıtlar silindi.", 200)

@app.route('/api/faces', methods=['POST'])
def users():
    face_list = []
    with open('./storage/db/face.data', 'rb') as filehandle:  
        face_list = pickle.load(filehandle)

    if not face_list:
       return success_handle("Kayıtlı kişi yok.")

    makeitastring = '<br/>'.join(map(str, face_list))   
    return success_handle(makeitastring)


# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
    #app.run()