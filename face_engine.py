import face_recognition
import cv2
import os
import numpy as np
import time
from PIL import Image

class FaceEngine:
    def __init__(self, authorized_dir="Authorized_Faces"):
        self.authorized_dir = authorized_dir
        self.known_face_encodings = []
        self.known_face_names = []
        
        if not os.path.exists(self.authorized_dir):
            os.makedirs(self.authorized_dir)
            
        self.load_authorized_faces()

    def sanitize_image(self, frame):
        """Forcefully converts any image frame to a dlib-compatible 8-bit RGB format."""
        # 1. Convert to RGB if it's BGR (from OpenCV)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # 2. Force to 8-bit unsigned integer
        rgb_8bit = np.array(rgb, dtype='uint8')
        # 3. Ensure it only has 3 channels (Red, Green, Blue) - No Alpha/Transparency
        return rgb_8bit[:, :, :3]

    def load_authorized_faces(self):
        for filename in os.listdir(self.authorized_dir):
            if filename.endswith((".jpg", ".png", ".jpeg")):
                path = os.path.join(self.authorized_dir, filename)
                try:
                    # Use OpenCV to load
                    img = cv2.imread(path)
                    if img is None: continue
                    
                    # Sanitize
                    clean_img = self.sanitize_image(img)
                    
                    # Encode
                    encodings = face_recognition.face_encodings(clean_img)
                    if encodings:
                        self.known_face_encodings.append(encodings[0])
                        self.known_face_names.append(os.path.splitext(filename)[0])
                        print(f"Success: Loaded {filename}")
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
                    
        print(f"Total authorized faces: {len(self.known_face_names)}")

    def recognize_user(self):
        video_capture = cv2.VideoCapture(0)
        # Give the camera 2 seconds to adjust brightness so the face is clear
        start_time = time.time()
        found_user = "Unknown"

        print("System: Looking for Master Bikal...")
        
        # Look for 3 seconds instead of just 1 frame
        while time.time() - start_time < 5:
            ret, frame = video_capture.read()
            if not ret: continue

            try:
                clean_frame = self.sanitize_image(frame)
                face_locations = face_recognition.face_locations(clean_frame)
                face_encodings = face_recognition.face_encodings(clean_frame, face_locations)

                for face_encoding in face_encodings:
                    # Tolerance 0.6 is the "Sweet Spot" for recognition
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.6)
                    if True in matches:
                        first_match_index = matches.index(True)
                        found_user = self.known_face_names[first_match_index]
                        video_capture.release()
                        return found_user
            except Exception as e:
                continue
        
        video_capture.release()
        return found_user

face_recognizer = FaceEngine()