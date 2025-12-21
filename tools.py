import pywhatkit
import os
from dotenv import load_dotenv
import webbrowser
import requests
import psutil
import pyautogui
import os
import time
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# --- YOUTUBE FEATURE ---
def play_music(song_name):
    try:
        cleaned_name = song_name.replace("play", "").strip()
        print(f"Searching YouTube for: {cleaned_name}")
        pywhatkit.playonyt(cleaned_name)
        return f"Playing {cleaned_name} on YouTube."
    except Exception as e:
        return f"I couldn't play the music because: {e}"

# --- WEB BROWSER FEATURE ---
def open_site(site_name):
    sites = {
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "facebook": "https://www.facebook.com",
        "gmail": "https://www.gmail.com"
    }
    
    url = sites.get(site_name.lower())
    if url:
        webbrowser.open(url)
        return f"Opening {site_name}."
    else:
        webbrowser.open(f"https://www.{site_name}.com")
        return f"Opening {site_name}."

# --- WEATHER FEATURE ---
def get_weather(city):
    api_key = os.getenv("WEATHER_API_KEY")
    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(base_url).json()
        if response["cod"] != "404":
            main = response["main"]
            weather_desc = response["weather"][0]["description"]
            temp = main["temp"]
            return f"The temperature in {city} is {temp} degrees Celsius with {weather_desc}."
        else:
            return f"I couldn't find the weather for {city}, Bikal."
    except Exception:
        return "I'm having trouble connecting to the weather service."

# --- SYSTEM MONITORING ---
def get_system_stats():
    battery = psutil.sensors_battery()
    percent = battery.percent
    plugged = battery.power_plugged
    cpu_usage = psutil.cpu_percent(interval=0.1) # Shorter interval for faster response
    
    status = f"Sir, the CPU usage is at {cpu_usage} percent. Battery is at {percent} percent. "
    status += "The charger is plugged in." if plugged else "The charger is not plugged in."
    return status, percent, plugged

def battery_alert():
    battery = psutil.sensors_battery()
    if battery and battery.percent < 20 and not battery.power_plugged:
        return "Warning Sir! Battery is below 20 percent. Please plug in the charger."
    return None

# --- SCREENSHOT FEATURE ---
def take_screenshot():
    if not os.path.exists("Screenshots"):
        os.makedirs("Screenshots")
    
    name = f"screenshot_{int(time.time())}.png"
    path = os.path.join("Screenshots", name)
    
    img = pyautogui.screenshot()
    img.save(path)
    return f"Screenshot saved successfully."

# --- BRIGHTNESS FEATURE ---
def set_brightness(level):
    try:
        brightness_val = int(level)
        # Ensure it stays between 0 and 100
        brightness_val = max(0, min(100, brightness_val))
        sbc.set_brightness(brightness_val)
        return f"Brightness set to {brightness_val} percent."
    except Exception as e:
        return f"Error changing brightness: {e}"

# --- VOLUME FEATURE (FIXED) ---
def set_volume(query):
    try:
        # If you say "100", we just maximize it. 
        # Since we can't set a specific % easily with keys, we use Up/Down.
        if "100" in query or "full" in query:
            for _ in range(50): # Press volume up 50 times
                pyautogui.press("volumeup")
            return "Volume set to maximum, Sir."
            
        elif "0" in query or "mute" in query:
            for _ in range(50): # Press volume down 50 times
                pyautogui.press("volumedown")
            return "Volume muted, Sir."
            
        elif "increase" in query or "up" in query:
            for _ in range(10): 
                pyautogui.press("volumeup")
            return "Increasing volume."
            
        elif "decrease" in query or "down" in query:
            for _ in range(10): 
                pyautogui.press("volumedown")
            return "Decreasing volume."
        
        else:
            # If you give a specific number, we'll just bump it up a bit
            for _ in range(5):
                pyautogui.press("volumeup")
            return "Adjusting volume for you."
            
    except Exception as e:
        return f"Could not adjust volume: {e}"