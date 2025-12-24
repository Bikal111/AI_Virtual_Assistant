import face_recognition
import cv2
import os
import numpy as np
import time
import ctypes

class FaceEngine:
    def __init__(self, authorized_dir="Authorized_Faces"):
        self.authorized_dir = authorized_dir
        self.known_face_encodings = []
        self.known_face_names = []
        
        if not os.path.exists(self.authorized_dir):
            os.makedirs(self.authorized_dir)
            
        self.load_authorized_faces()

    def sanitize_image(self, frame):
        """Standardizes image format for face_recognition/dlib."""
        try:
            # Convert BGR (OpenCV) to RGB
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Force to 8-bit unsigned integer (Fixes Numpy 2.0+ compatibility)
            return np.array(rgb, dtype='uint8')
        except Exception as e:
            print(f"Sanitization Error: {e}")
            return None

    def load_authorized_faces(self):
        """Loads all images from the directory. Every file is a new user."""
        print("System: Loading Authorized Personnel...")
        for filename in os.listdir(self.authorized_dir):
            if filename.lower().endswith((".jpg", ".png", ".jpeg")):
                path = os.path.join(self.authorized_dir, filename)
                try:
                    img = cv2.imread(path)
                    if img is None: continue
                    
                    clean_img = self.sanitize_image(img)
                    encodings = face_recognition.face_encodings(clean_img)
                    
                    if encodings:
                        self.known_face_encodings.append(encodings[0])
                        # Name is taken from the filename (e.g., 'Bikal.jpg' -> 'Bikal')
                        self.known_face_names.append(os.path.splitext(filename)[0])
                        print(f"Successfully Authorized: {os.path.splitext(filename)[0]}")
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
        
        print(f"Total Authorized Users: {len(self.known_face_names)}")

    def recognize_user(self):
        """Scans for 5 seconds. Returns the name or 'Unknown'."""
        video_capture = cv2.VideoCapture(0)
        start_time = time.time()
        
        print("System: Initiating Biometric Scan. Please look at the camera...")
        
        while time.time() - start_time < 5:
            ret, frame = video_capture.read()
            if not ret: continue

            clean_frame = self.sanitize_image(frame)
            face_locations = face_recognition.face_locations(clean_frame)
            face_encodings = face_recognition.face_encodings(clean_frame, face_locations)

            for face_encoding in face_encodings:
                # Tolerance 0.5 is stricter for better security
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.8)
                if True in matches:
                    first_match_index = matches.index(True)
                    user_name = self.known_face_names[first_match_index]
                    video_capture.release()
                    return user_name
        
        video_capture.release()
        return "Unknown"

    def lock_workstation(self):
        """Locks the Windows PC."""
        print("System: Security Breach! Locking Workstation.")
        ctypes.windll.user32.LockWorkStation()

# Initialize the engine
face_recognizer = FaceEngine()