import face_recognition
from os import path
import cv2
import sys
import os
import pickle
import base64
import yaml

class Face:
    def __init__(self, app):
        self.storage = app.config["storage"]
        self.faces = []
        self.known_encoding_faces = []
        self.face_user_keys = {}
        self.train_dataset()
        self.known_face_name_list = []



    def load_train_file_by_name(self, name):
        trained_storage = path.join(self.storage, 'trained')
        return path.join(trained_storage, name)

    def load_unknown_file_by_name(self, name):
        unknown_storage = path.join(self.storage, 'unknown')
        return path.join(unknown_storage, name)

    def recognize(self, unknown_filename):
       
        with open('./storage/db/face.data', 'rb') as filehandle:  
            known_face_name_list_local = pickle.load(filehandle)

        with open('config.yaml', 'r') as f:
            cfg = yaml.load(f)

        # face_rec parameter values from config file
        val_number_of_times_to_upsample = cfg["number_of_times_to_upsample"]
        val_model =  cfg["model"]
        val_num_jitters=  cfg["num_jitters"]
        val_tolerans=  cfg["tolerans"]

        cvframe = cv2.imread(self.load_unknown_file_by_name(unknown_filename))
        small_frame = cv2.resize(cvframe, (0, 0), fx=0.25, fy=0.25)
        small_rgb_frame = small_frame[:, :, ::-1]

        # get face location
        face_locations = face_recognition.face_locations(small_rgb_frame, number_of_times_to_upsample = val_number_of_times_to_upsample , model= val_model)


        face_encodings = face_recognition.face_encodings(small_rgb_frame, face_locations, num_jitters= val_num_jitters)

        # face_encodings = face_recognition.face_encodings (face_image, num_jitters = 100 ) titreme ile doğruluğu arttır
        face_names = []

        for face_encoding in face_encodings:
            # results = face_recognition.compare_faces (known_face_encodings, face_encoding, tolerans = 0.5 ) threshold değeri
            matches = face_recognition.compare_faces(self.known_encoding_faces, face_encoding)
            name = "bilinmeyen"  # default name is not recognized
            
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_name_list_local[first_match_index]
                
            print("Detected face: " + name, file=sys.stdout)
            face_names.append(name)

        # draw name
        result_frame = self.draw_rectangle_on_image(cvframe, face_locations, face_names)
        
        # convert base64
        retval, buffer = cv2.imencode('.jpg', result_frame)
        jpg_as_text = base64.b64encode(buffer)
        return jpg_as_text
        
        # result
        ''' faceNames = ''.join(face_names)
        count = str(len(face_locations))
        location = ','.join([str(i) for i in face_locations])


        print("---- Recognized Completed ----", file=sys.stdout)
        return faceNames'''

    def train_dataset(self):
        print("---- Training Started ----", file=sys.stdout)
        known_face_name_list_local =[]
        for root, dirs, files in os.walk("./storage/trained/"):
            for filename in files:
                file_result = filename.split("_")
                if not file_result:
                    continue
                customer_name = file_result[0].split(".")
                if not customer_name:
                    continue
                known_face_name_list_local.append(customer_name[0])
                image = face_recognition.load_image_file("./storage/trained/"+filename)
                face_encodings_images = face_recognition.face_encodings(image)
                if not face_encodings_images:
                    continue
                image_face_encoding = face_encodings_images[0]
                self.known_encoding_faces.append(image_face_encoding)

        with open('./storage/db/face.data', 'wb') as filehandle:  
            pickle.dump(known_face_name_list_local, filehandle)
        
        print("---- Training Completed ----", file=sys.stdout)

    def draw_rectangle_on_image(self, frame, face_locations, face_names):
    
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (153, 0, 51), 4)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, top + 35),
                          (right, top), (153, 0, 51), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 10, top + 25),
                        font, 1.0, (255, 255, 255), 2)
        # write temp image file for lblimage item
        return frame

