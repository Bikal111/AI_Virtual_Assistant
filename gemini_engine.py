import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv() # This loads the variables from .env
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

def ask_gemini(prompt):
    try:
        # We are using the exact name from your check_models list
        model = genai.GenerativeModel('models/gemini-2.5-flash') 
        
        # Adding a persona helps Jarvis sound more like an assistant
        full_prompt = f"You are Jarvis, a helpful AI assistant. Answer this in one short sentence: {prompt}"
        
        response = model.generate_content(full_prompt)
        
        # Return the clean text response
        return response.text
            
    except Exception as e:
        print(f"Gemini Error: {e}")
        return "I am having trouble accessing my knowledge base."