import pyttsx3
import speech_recognition as sr
import datetime
import webbrowser
import os
import time
import psutil
from gemini_engine import ask_gemini 
from tools import play_music, open_site, get_weather, get_system_stats, battery_alert, take_screenshot, set_brightness, set_volume 

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
    wishMe()
    last_plugged_state = psutil.sensors_battery().power_plugged # Remember current state

    while True:
        # Check if charger state changed
        current_plugged_state = psutil.sensors_battery().power_plugged
        if last_plugged_state == True and current_plugged_state == False:
            speak("Sir, the charger has been disconnected.")
        elif last_plugged_state == False and current_plugged_state == True:
            speak("Charging started. Thank you, Sir.")
            
        last_plugged_state = current_plugged_state
        query = takeCommand()
        alert = battery_alert()
        if alert:
            speak(alert)

        if query == "none":
            continue

        # --- USING THE TOOLS FILE ---
        if 'play' in query:
            response = play_music(query)
            speak(response)

        elif 'open' in query:
            # If the user says "open youtube", we send "youtube" to our tool
            site = query.replace("open", "").strip()
            response = open_site(site)
            speak(response)

        elif 'the time' in query:
            strTime = datetime.datetime.now().strftime("%I:%M %p")
            speak(f"Sir, the time is {strTime}")
        
        elif 'weather' in query:
            # We assume the user says "weather in Kathmandu"
            # We split the string to get the city name
            city = query.split("in")[-1].strip()
            if city == "weather": # If user just says "weather" without a city
                city = "Lalitpur" # Set your default city
            
            report = get_weather(city)
            speak(report)
        
        elif 'system status' in query or 'battery' in query:
            stats, percent, plugged = get_system_stats()
            speak(stats)
        
        elif 'screenshot' in query:
            speak("Taking a screenshot")
            time.sleep(0) # Gives you time to switch windows
            report = take_screenshot()
            speak(report)
        elif 'brightness' in query:
            level = "".join(filter(str.isdigit, query))
            if level:
                speak(set_brightness(level))
            else:
                speak("Sir, what level of brightness should I set?")
        elif 'volume' in query:
            # We pass the WHOLE query so the function can look for "up" or "100"
            report = set_volume(query)
            speak(report)
        

        elif 'exit' in query or 'stop' in query:
            speak("Goodbye Bikal!")
            break

        # --- GEMINI BRAIN ---
        else:
            speak("Let me think...")
            reply = ask_gemini(query)
            speak(reply)
        