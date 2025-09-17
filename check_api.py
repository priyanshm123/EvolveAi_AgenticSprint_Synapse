import os
import google.generativeai as genai
import sys

print("--- Checking Gemini API Key Configuration ---")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: GEMINI_API_KEY environment variable is not set.")
    print("Please set it in your terminal before running this script.")
    print("Example (macOS/Linux): export GEMINI_API_KEY='YOUR_API_KEY'")
    print("Example (Windows): set GEMINI_API_KEY='YOUR_API_KEY'")
    sys.exit(1)

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = "Give me a single word that describes the color of the sky on a clear day."
    print(f"Attempting to call the Gemini API with a test prompt: '{prompt}'")
    
    response = model.generate_content(prompt)
    
    print("\n--- API Call Successful ---")
    print("Raw Response Text:")
    print(response.text)
    
except Exception as e:
    print("\n--- API Call Failed ---")
    print(f"An error occurred: {e}")
    if "401" in str(e):
        print("This is often a 401 Unauthorized error, which means your API key is invalid or not active.")