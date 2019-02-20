import face_recognition
from os import path
import cv2
import sys
import os

class Face:
    def __init__(self, app):
        self.storage = app.config["storage"]
        self.db = app.db
        self.faces = []  # storage all faces in caches array of face object
        self.known_encoding_faces = []  # faces data for recognition
        self.face_user_keys = {}
        self.load_all()
        self.known_face_name_list = []


    def load_user_by_index_key(self, index_key=0):

        key_str = str(index_key)

        if key_str in self.face_user_keys:
            return self.face_user_keys[key_str]

        return None

    def load_train_file_by_name(self, name):
        trained_storage = path.join(self.storage, 'trained')
        return path.join(trained_storage, name)

    def load_unknown_file_by_name(self, name):
        unknown_storage = path.join(self.storage, 'unknown')
        return path.join(unknown_storage, name)

    def train_load_all(self):

        results = self.db.select('SELECT faces.id, faces.user_id, faces.filename, faces.created FROM faces')

        for row in results:

            user_id = row[1]
            filename = row[2]

            face = {
                "id": row[0],
                "user_id": user_id,
                "filename": filename,
                "created": row[3]
            }
            self.faces.append(face)

            face_image = face_recognition.load_image_file(self.load_train_file_by_name(filename))
            face_image_encoding = face_recognition.face_encodings(face_image)[0]
            index_key = len(self.known_encoding_faces)
            self.known_encoding_faces.append(face_image_encoding)
            index_key_string = str(index_key)
            self.face_user_keys['{0}'.format(index_key_string)] = user_id

    def faceRecognitionFromPicture(self, unknown_filename):
        unknown_image = face_recognition.load_image_file(self.load_unknown_file_by_name(unknown_filename))
        unknown_encoding_image = face_recognition.face_encodings(unknown_image)[0]

        results = face_recognition.compare_faces(self.known_encoding_faces, unknown_encoding_image);

        print("results", results)

        index_key = 0
        for matched in results:

            if matched:
                # so we found this user with index key and find him
                user_id = self.load_user_by_index_key(index_key)

                return user_id

            index_key = index_key + 1

        return None

    def recognize(self, unknown_filename):
        cvframe = cv2.imread(self.load_unknown_file_by_name(unknown_filename))

        small_frame = cv2.resize(cvframe, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        small_rgb_frame = small_frame[:, :, ::-1]

        # get face location
        face_locations = face_recognition.face_locations(small_rgb_frame, number_of_times_to_upsample = 1 , model="hog")
        # face_locations = face_recognition.face_locations(small_rgb_frame, model='hog' model='cnn') farklı tespit modelleri
        # face_locations = face_recognition.face_locations (rgb_frame, number_of_times_to_upsample = 2 ) daha uzak yüzler
        print("- Face location scan completed", file=sys.stdout)

        face_encodings = face_recognition.face_encodings(small_rgb_frame, face_locations, num_jitters=2)

        # face_encodings = face_recognition.face_encodings (face_image, num_jitters = 100 ) titreme ile doğruluğu arttır
        face_names = []

        for face_encoding in face_encodings:
            # results = face_recognition.compare_faces (known_face_encodings, face_encoding, tolerans = 0.5 ) threshold değeri
            matches = face_recognition.compare_faces(self.known_encoding_faces, face_encoding)
            name = "Unknown Customer"  # default name is not recognized
            
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]
                print("DETECTED FACE > " + name, file=sys.stdout)

            face_names.append(name)


        print("- Face Locations:", file=sys.stdout)
        # print face data
        print(*face_locations, sep='\n')
        print(*face_names, sep='\n')
        print("- Face name searching completed", file=sys.stdout)
        # Label string
        faceNames = ''.join(face_names)
        count = str(len(face_locations))
        location = ','.join([str(i) for i in face_locations])
        return_string = "\nCustomers: "+faceNames + \
            "\nFace Count: "+count+"\nLocations: "+location+"\n"
        print(return_string, file=sys.stdout)
        print("---- Recognized Completed ----", file=sys.stdout)
        return None

    def load_all(self):
        print("---- Training Started ----", file=sys.stdout)
        for root, dirs, files in os.walk("./storage/trained/"):
            for filename in files:
                file_result = filename.split("_")
                customer_name = file_result[0].split(".")
                print("Customer Name: " + file_result[0], file=sys.stdout)
                self.known_face_name_list.append(customer_name[0])
                image = face_recognition.load_image_file("./storage/trained/"+filename)
                image_face_encoding = face_recognition.face_encodings(image)[0]
                self.known_encoding_faces.append(image_face_encoding)

        print("---- Training Completed ----", file=sys.stdout)
