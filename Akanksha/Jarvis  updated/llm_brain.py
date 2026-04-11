from google import genai
from google.genai import types
import pyttsx3
import re
import socket
import concurrent.futures

# 🌐 IPv4 Force Patch (Fixes TCP Handshake hangs)
_old_getaddrinfo = socket.getaddrinfo
def new_getaddrinfo(*args, **kwargs):
    responses = _old_getaddrinfo(*args, **kwargs)
    return [r for r in responses if r[0] == socket.AF_INET]
socket.getaddrinfo = new_getaddrinfo

API_KEY = "AIzaSyCNWjskQIpk0gHwTvX8gBsFcW8xdZ005Z4" 

client = genai.Client(
    api_key=API_KEY,
    http_options=types.HttpOptions(timeout=120 * 1000)
)

# 🔥 JARVIS SHORT-TERM MEMORY
chat_memory = []

def say(text):
    """Creates a fresh engine each time to prevent deadlocks."""
    try:
        temp_engine = pyttsx3.init()
        temp_engine.say(text)
        temp_engine.runAndWait()
        temp_engine.stop()
    except Exception as e:
        print(f"⚠️ Speech Error: {e}")

def ask_jarvis_llm(prompt):
    global chat_memory
    print("🧠 JARVIS is thinking...")
    
    # Add prompt to memory
    chat_memory.append(f"User: {prompt}")

    # Keep only the last 4 interactions
    if len(chat_memory) > 4:
        chat_memory.pop(0)

    conversation_history = "\n".join(chat_memory)
    
    context = (
        "You are JARVIS, a witty AI. Keep answers under 3 sentences. "
        "No markdown. Here is the recent conversation:\n"
        f"{conversation_history}\nJARVIS:"
    )

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        # 🔥 USING THE LITE MODEL TO BYPASS 503 SERVER ERRORS
        future = executor.submit(
            client.models.generate_content, 
            model='gemini-2.5-flash-lite', 
            contents=context
        )
        
        try:
            response = future.result(timeout=20.0) 
            clean_text = re.sub(r'[*#_]', '', response.text).strip()
            print(f"🤖 JARVIS: {clean_text}")
            
            # Add JARVIS's answer to memory
            chat_memory.append(f"JARVIS: {clean_text}")
            
            say(clean_text) 
            return True

        except concurrent.futures.TimeoutError:
            print("❌ Request timed out! (Server Load or Local Network)")
            return False
        except Exception as e:
            # 🔥 SPOKEN 503 ERROR MESSAGE
            if "503" in str(e):
                print("❌ JARVIS Brain Error: Google's servers are overloaded (503).")
                say("I'm sorry, my cloud connection is currently congested. Please try again in a moment.")
            else:
                print(f"❌ JARVIS Brain Error: {e}")
            return False