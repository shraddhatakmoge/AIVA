# from google import genai
# import pyttsx3
# import re

# # 🔥 PASTE YOUR ACTUAL KEY HERE (Keep the quotes!)
# # Example: API_KEY = "AIzaSyB-1234567890abcdefg..."
# API_KEY = "AIzaSyC8MWSLp9NcKIiS1i8kySq-SF9Z0QSq4b4"

# # Initialize the NEW Google GenAI Client
# client = genai.Client(api_key=API_KEY)
# engine = pyttsx3.init()

# def ask_jarvis_llm(prompt):
#     print("🧠 JARVIS is thinking...")
#     try:
#         # The System Prompt
#         context = (
#             "You are JARVIS, a highly advanced, witty AI assistant created by an AI & DS Engineering student. "
#             "Keep your answers extremely concise, conversational, and strictly under 3 sentences. "
#             "Do not use asterisks, bolding, or markdown in your response. "
#             f"User asks: {prompt}"
#         )
        
#         # Using the newest, fastest model available in the new SDK
#         response = client.models.generate_content(
#             model='gemini-2.5-flash', 
#             contents=context
#         )
        
#         # Clean up any leftover markdown characters
#         clean_text = re.sub(r'[*#_]', '', response.text).strip()
        
#         print(f"🤖 JARVIS: {clean_text}")
        
#         # Speak the answer
#         engine.say(clean_text)
#         engine.runAndWait()
        
#         return True
        
#     except Exception as e:
#         print(f"❌ JARVIS Brain Error: {e}")
#         engine.say("I'm sorry, I am having trouble connecting to my neural network right now.")
#         engine.runAndWait()
#         return False