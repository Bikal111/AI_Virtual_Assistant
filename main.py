import pyttsx3
import speech_recognition as sr
import datetime
import webbrowser
import cv2
import os
import time
import psutil
from gemini_engine import ask_gemini 
from tools import play_music, open_site, get_weather, get_system_stats, battery_alert, take_screenshot, set_brightness, set_volume 
from vision_engine import vision # Simple and clean!
from face_engine import face_recognizer
from alerts import send_telegram_alert
import threading

# --- STEP 1: DEFINE THE ENGINE HELPER ---
def get_engine():
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    engine.setProperty('rate', 180)
    return engine

# --- STEP 2: DEFINE THE SPEAK FUNCTION ---
def speak(audio):
    print(f"Jarvis: {audio}")
    try:
        engine = get_engine()
        engine.say(audio)
        engine.runAndWait()
    except Exception as e:
        print(f"Speech Error: {e}")

# --- STEP 3: DEFINE OTHER FUNCTIONS ---
def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak("Good Morning Bikal!")
    elif hour >= 12 and hour < 18:
        speak("Good Afternoon Bikal!")
    else:
        speak("Good Evening Bikal!")
    speak("I am online. Wake we when i am needed")

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nListening...")
        r.pause_threshold = 0.8
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.listen(source)

    try:
        print("Recognizing...")    
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
    except Exception:
        return "none"
    return query.lower()

# --- STEP 4: THE MAIN LOOP ---
if __name__ == "__main__":
    print("System: Jarvis is Online and in Sleep Mode...")
    
    # --- STEP 1: BIOMETRIC SLEEP LOOP (Watching for Face) ---
    while True:
        user = face_recognizer.recognize_user()
        
        if user != "Unknown" and user != "None":
            wishMe() 
            speak(f"Authentication successful. Standing by for your command, Master {user.capitalize()}.")
            break # Breaks to enter Standby/Active states
            
        elif user == "Unknown":
            print("CRITICAL: Unauthorized User Detected!")
            cap = cv2.VideoCapture(0)
            time.sleep(1.5) 
            for _ in range(8): cap.read() 
            ret, frame = cap.read()
            cap.release()
            
            if ret and frame is not None:
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                intruder_photo = f"Intruders/intruder_{timestamp}.jpg"
                if not os.path.exists("Intruders"): os.makedirs("Intruders")
                cv2.imwrite(intruder_photo, frame)
                
                from alerts import send_telegram_alert
                threading.Thread(target=send_telegram_alert, args=(intruder_photo,)).start()
            
            speak("Unauthorized access detected. Locking system and alerting Master Bikal.")
            face_recognizer.lock_workstation()
            exit()
        else:
            print("System: Sleep Mode... Monitoring...")
            time.sleep(1)

    # --- STEP 2: SYSTEM MONITORING SETUP ---
    last_plugged_state = psutil.sensors_battery().power_plugged

    # --- STEP 3: STANDBY & ACTIVE COMMAND LOOP ---
    while True:
        # A. Charger Monitoring (Always active in background)
        current_plugged_state = psutil.sensors_battery().power_plugged
        if last_plugged_state != current_plugged_state:
            if current_plugged_state:
                speak("Charging started. Thank you, Sir.")
            else:
                speak("Sir, the charger has been disconnected.")
            last_plugged_state = current_plugged_state

        # B. STANDBY CHECK: Listen for "Hey Jarvis"
        print("System: Standby Mode - Awaiting Wake Word...")
        wake_query = takeCommand().lower()

        if "hey jarvis" in wake_query:
            speak("At your service, Sir.")
            active_start_time = time.time() # Start the 30s timer

            # --- STEP 4: ACTIVE COMMAND MODE ---
            while True:
                # Check for 30 seconds of inactivity
                elapsed_time = time.time() - active_start_time
                if elapsed_time > 30:
                    speak("System entering standby due to thirty seconds of inactivity.")
                    break # Drops back to "Hey Jarvis" standby

                query = takeCommand().lower()

                if query == "none":
                    continue

                # Reset the activity timer because you spoke
                active_start_time = time.time()

                # --- D. COMMAND PROCESSING ---
                if 'play' in query:
                    speak(play_music(query))

                elif 'open' in query:
                    site = query.replace("open", "").strip()
                    speak(open_site(site))

                elif 'the time' in query:
                    strTime = datetime.datetime.now().strftime("%I:%M %p")
                    speak(f"Sir, the time is {strTime}")
                
                elif 'weather' in query:
                    city = query.split("in")[-1].strip()
                    if city == "weather": city = "Lalitpur" 
                    speak(get_weather(city))
                
                elif 'system status' in query or 'battery' in query:
                    stats, _, _ = get_system_stats()
                    speak(stats)
                
                elif 'screenshot' in query:
                    speak("Taking a screenshot")
                    speak(take_screenshot())

                elif 'brightness' in query:
                    level = "".join(filter(str.isdigit, query))
                    speak(set_brightness(level) if level else "What level, Sir?")

                elif 'volume' in query:
                    speak(set_volume(query))
                
                elif 'what do you see' in query or 'look at this' in query:
                    speak("Scanning the area, Sir...")
                    speak(vision.analyze_scene("Describe the objects and person clearly."))

                elif 'secure the room' in query or 'sentinel mode' in query:
                    speak("Activating Sentinel Mode.")
                    if face_recognizer.sentinel_scan():
                        speak("Unauthorized access detected. System secured.")
                
                elif 'go to sleep' in query or 'standby' in query:
                    speak("Entering biometric sleep mode. Restarting watchdog.")
                    os.system("python main.py") # Fully resets to Step 1
                    exit()
                
                elif 'exit' in query or 'stop' in query:
                    speak("Goodbye Bikal!")
                    exit()

                else:
                    speak("Searching my database...")
                    speak(ask_gemini(query))