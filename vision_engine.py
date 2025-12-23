import cv2
import PIL.Image
import google.generativeai as genai
import os
import time
from dotenv import load_dotenv

load_dotenv()

class VisionManager:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=self.api_key)
        # Using the exact version from your list
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def capture_image(self):
        cam = cv2.VideoCapture(0)
        time.sleep(1) # Let camera adjust
        ret, frame = cam.read()
        if ret:
            path = "vision_temp.jpg"
            cv2.imwrite(path, frame)
            cam.release()
            return path
        cam.release()
        return None

    def analyze_scene(self, prompt="Describe what you see."):
        image_path = self.capture_image()
        if image_path:
            try:
                # 1. Open and load the image safely
                img = PIL.Image.open(image_path)
                
                # 2. Generate content
                response = self.model.generate_content([prompt, img])
                
                # 3. Close the image object manually before deleting
                img.close() 
                
                # 4. Delete file
                if os.path.exists(image_path):
                    os.remove(image_path)
                    
                return response.text
            except Exception as e:
                # If deletion fails here, we still want to know why
                return f"Sir, I can't process the image: {e}"
        return "Sir, I am unable to access my visual sensors."

vision = VisionManager()