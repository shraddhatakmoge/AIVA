# import pyautogui
# import time

# print("Tracking mouse... Press Ctrl+C to stop.")
# try:
#     while True:
#         x, y = pyautogui.position()
#         print(f"X: {x} | Y: {y}", end="\r")
#         time.sleep(0.1)
# except KeyboardInterrupt:
#     print("\nDone.")
import google.generativeai as genai

# 🔥 Paste your API key here
API_KEY = "YAIzaSyC8MWSLp9NcKIiS1i8kySq-SF9Z0QSq4b4"
genai.configure(api_key=API_KEY)

print("🔍 Scanning for available Gemini models...\n")

try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ Found Model: {m.name}")
except Exception as e:
    print(f"❌ Connection Error: {e}")