import pyttsx3
import speech_recognition as sr
import datetime
import webbrowser
import os
import time
import psutil
from gemini_engine import ask_gemini 
from tools import play_music, open_site, get_weather, get_system_stats, battery_alert, take_screenshot, set_brightness, set_volume 
from vision_engine import vision # Simple and clean!
from face_engine import face_recognizer

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
    speak("I am online. How can I help you?")

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
    # --- STEP 1: AUTHENTICATION ---
    print("System: Initializing Face Recognition...")
    # This now uses the 3-second scanning loop we discussed
    user = face_recognizer.recognize_user()
    
    if user != "Unknown" and user != "None":
        # Authentication Success
        wishMe() 
        speak(f"Authentication successful. Welcome back, Master {user.capitalize()}.")
        print(f"Access Granted: {user}")
    else:
        # Authentication Failed
        speak("Biometric scan failed. Access restricted to guest mode.")
        wishMe() # Jarvis greets as Guest or uses the generic greeting
        print("Access Level: Guest")

    # --- STEP 2: SYSTEM MONITORING SETUP ---
    last_plugged_state = psutil.sensors_battery().power_plugged 

    # --- STEP 3: MAIN COMMAND LOOP ---
    while True:
        # A. Charger Monitoring
        current_plugged_state = psutil.sensors_battery().power_plugged
        if last_plugged_state == True and current_plugged_state == False:
            speak("Sir, the charger has been disconnected.")
        elif last_plugged_state == False and current_plugged_state == True:
            speak("Charging started. Thank you, Sir.")
        last_plugged_state = current_plugged_state
        
        # B. Battery Health Alert
        alert = battery_alert()
        if alert:
            speak(alert)

        # C. Listen for Command
        query = takeCommand()

        if query == "none":
            continue

        # --- D. COMMAND PROCESSING ---
        
        # 1. Multimedia & Entertainment
        if 'play' in query:
            response = play_music(query)
            speak(response)

        elif 'open' in query:
            site = query.replace("open", "").strip()
            response = open_site(site)
            speak(response)

        # 2. Information & Utilities
        elif 'the time' in query:
            strTime = datetime.datetime.now().strftime("%I:%M %p")
            speak(f"Sir, the time is {strTime}")
        
        elif 'weather' in query:
            city = query.split("in")[-1].strip()
            if city == "weather": 
                city = "Lalitpur" 
            report = get_weather(city)
            speak(report)
        
        elif 'system status' in query or 'battery' in query:
            stats, percent, plugged = get_system_stats()
            speak(stats)
        
        # 3. Hardware Control
        elif 'screenshot' in query:
            speak("Taking a screenshot")
            report = take_screenshot()
            speak(report)

        elif 'brightness' in query:
            level = "".join(filter(str.isdigit, query))
            if level:
                speak(set_brightness(level))
            else:
                speak("Sir, what level of brightness should I set?")

        elif 'volume' in query:
            report = set_volume(query)
            speak(report)
        
        # 4. Vision Engine (The Eyes)
        elif 'what do you see' in query or 'look at this' in query:
            speak("Scanning the area, Sir...")
            # Using prompt to Gemini
            # Ensure vision_engine.py is using 'gemini-1.5-flash' to avoid quota error
            description = vision.analyze_scene("Describe the objects and person clearly.")
            speak(description)
        
        # 5. Exit Jarvis
        elif 'exit' in query or 'stop' in query:
            speak("Goodbye Bikal!")
            break

        # 6. Gemini Intelligence (Brain)
        else:
            speak("Searching my database...")
            reply = ask_gemini(query)
            speak(reply)