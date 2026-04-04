import os
import time
import pyautogui
import pygetwindow as gw
import pyperclip
import pyttsx3
import threading



pyautogui.FAILSAFE = False

last_message = ""
engine = pyttsx3.init()

def speak(text):
    print("🔊", text)
    engine.say(text)
    engine.runAndWait()


# -------- OPEN --------
def open_whatsapp():
    os.system("start shell:AppsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App")
    time.sleep(3)


# -------- CLOSE --------
def close_whatsapp():


    # Try process kill
    os.system("taskkill /f /im WhatsApp.exe >nul 2>&1")

    # Fallback: close by window title
    os.system('taskkill /f /fi "WINDOWTITLE eq WhatsApp*" >nul 2>&1')

    print("✅ WhatsApp closed")

# -------- FOCUS --------
def focus_whatsapp():
    windows = gw.getWindowsWithTitle("WhatsApp")

    for win in windows:
        try:
            if win.isMinimized:
                win.restore()
            win.activate()
            time.sleep(1)
            return True
        except:
            continue

    open_whatsapp()
    return False


# -------- SEND --------
def send_message(text):
    global last_message

    focus_whatsapp()
    time.sleep(1)

    pyautogui.write(text, interval=0.05)
    pyautogui.press("enter")

    last_message = text
    print("📤 Sent:", text)


# -------- SEND TO CONTACT --------
def send_message_to(contact, text):
    global last_message

    focus_whatsapp()
    time.sleep(2)

    pyautogui.hotkey("ctrl", "f")
    time.sleep(1)

    pyautogui.write(contact)
    time.sleep(2)

    pyautogui.press("down")
    pyautogui.press("enter")
    time.sleep(1)

    pyautogui.write(text)
    pyautogui.press("enter")

    last_message = text
    print(f"📤 Sent to {contact}: {text}")


# =========================================
# 🚀 NEW FEATURES START HERE
# =========================================


# -------- SEND SCREENSHOT --------
import os
import time
import io
from PIL import Image
import win32clipboard
import pyautogui

def get_latest_screenshot(folder):
    files = [os.path.join(folder, f) for f in os.listdir(folder)
             if f.lower().endswith((".png", ".jpg", ".jpeg"))]

    if not files:
        return None

    latest_file = max(files, key=os.path.getctime)
    return latest_file


def send_screenshot(contact):
    focus_whatsapp()
    time.sleep(1)

    # 🔥 Step 1: Set your screenshot folder
    folder = r"C:\Users\Akanksha\OneDrive\Pictures\Screenshots"   # 🔧 CHANGE if needed

    path = get_latest_screenshot(folder)

    if not path:
        print("❌ No screenshot found")
        speak("No screenshot found")
        return

    print("📸 Sending:", path)

    # 🔥 Step 2: Load image
    img = Image.open(path)

    # 🔥 Step 3: Copy to clipboard
    output = io.BytesIO()
    img.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]
    output.close()

    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()

    # 🔥 Step 4: Open chat
    pyautogui.hotkey("ctrl", "f")
    time.sleep(1)

    pyautogui.write(contact)
    time.sleep(2)

    pyautogui.press("down")
    pyautogui.press("enter")
    time.sleep(1)

    # 🔥 Step 5: Paste image
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1)

    pyautogui.press("enter")

    print("✅ Latest screenshot sent")

# --------- VOICE CALL ---------
def voice_call(contact):
    focus_whatsapp()
    time.sleep(1)

    # 🔥 Close anything
    for _ in range(2):
        pyautogui.press("esc")
        time.sleep(0.3)

    # 🔍 Open search
    pyautogui.hotkey("ctrl", "f")
    time.sleep(1)

    # 🔥 CLEAR SEARCH (IMPORTANT)
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.2)
    pyautogui.press("backspace")
    time.sleep(0.3)

    # 🔥 Type contact
    pyautogui.write(contact, interval=0.05)
    time.sleep(2)

    pyautogui.press("enter")
    time.sleep(2)


    pyautogui.press("esc")
    time.sleep(0.5)

    # Navigate to call
    for _ in range(9):
        pyautogui.press("tab")
        time.sleep(0.2)

    pyautogui.press("enter")

    for _ in range(7):
        pyautogui.press("tab")
        time.sleep(0.2)

    pyautogui.press("enter")
    
    pyautogui.moveTo(984, 600)  # 👈 replace with your coords
    time.sleep(0.5)
    pyautogui.click()

    print("📞 Voice calling", contact)


# ------ VIDEO CALL -------    
def video_call(contact):
    focus_whatsapp()
    time.sleep(1)

    # 🔥 Close anything
    for _ in range(2):
        pyautogui.press("esc")
        time.sleep(0.3)

    # 🔍 Open search
    pyautogui.hotkey("ctrl", "f")
    time.sleep(1)

    # 🔥 CLEAR SEARCH (IMPORTANT)
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.2)
    pyautogui.press("backspace")
    time.sleep(0.3)

    # 🔥 Type contact
    pyautogui.write(contact, interval=0.05)
    time.sleep(2)

    pyautogui.press("enter")
    time.sleep(2)

    for _ in range(9):
        pyautogui.press("tab")
        time.sleep(0.2)

    pyautogui.press("enter")

    for _ in range(6):
        pyautogui.press("tab")
        time.sleep(0.2)

    pyautogui.press("enter")
    
    pyautogui.moveTo(984, 600)  # 👈 replace with your coords
    time.sleep(0.5)
    pyautogui.click()

    print("🎥 Video calling", contact)
    
# ----- MUTE/UNMUTE CALL ------------   
def mute_call():
    pyautogui.hotkey("win", "alt", "k")

def unmute_call():
    pyautogui.hotkey("win", "alt", "k")
    
        
# ---------- CHECK STATUS ---------      
def open_status_by_click(contact):

    open_whatsapp()
    time.sleep(2)

    # 🔥 Step 1: CLOSE anything (search/chat)
    for _ in range(2):
        pyautogui.press("esc")
        time.sleep(0.3)

    # 🔥 Step 2: Open search
    pyautogui.hotkey("ctrl", "f")
    time.sleep(1)

    # 🔥 Step 3: CLEAR OLD TEXT
    pyautogui.hotkey("ctrl", "a")   # select all
    time.sleep(0.3)
    pyautogui.press("backspace")    # delete
    time.sleep(0.3)

    # 🔥 Step 4: TYPE CONTACT
    pyautogui.write(contact)
    time.sleep(2)

    # 🔥 Step 5: CLICK YOUR COORDINATES
    pyautogui.moveTo(165, 412)  # 👈 replace with your coords
    time.sleep(0.5)
    pyautogui.click()

    print("👁️ Status opened")
    
# -------- VOICE MESSAGE -----------
def send_voice_message(contact):
    thread = threading.Thread(target=_record_voice, args=(contact,))
    thread.start()


def _record_voice(contact):
    global STOP_RECORDING
    STOP_RECORDING = False

    focus_whatsapp()
    time.sleep(1)

    for _ in range(2):
        pyautogui.press("esc")
        time.sleep(0.3)

    pyautogui.hotkey("ctrl", "alt", "/")
    time.sleep(1)

    pyautogui.hotkey("ctrl", "a")
    pyautogui.press("backspace")

    pyautogui.write(contact, interval=0.05)
    time.sleep(2)

    pyautogui.press("enter")
    time.sleep(2)

    print("➡️ Chat opened")

    pyautogui.moveTo(1848, 955)
    time.sleep(0.5)

    # 🎤 Start recording
    pyautogui.mouseDown()
    print("🎙️ Recording...")

    # 🔥 Wait until STOP command comes
    while not STOP_RECORDING:
        time.sleep(0.2)

    # 🛑 Stop recording
    pyautogui.mouseUp()

    print("✅ Voice message sent")
    
def stop_voice_message():
    global STOP_RECORDING

    # 🔥 Set flag to stop loop
    STOP_RECORDING = True

    time.sleep(0.5)

    # 🔥 Bring WhatsApp to front
    focus_whatsapp()
    time.sleep(1)

    # 🎯 Move to your mic/send button
    pyautogui.moveTo(1848, 955)  # your coordinates
    time.sleep(0.3)

    # 🔥 Click to ensure send
    pyautogui.click()

    print("✅ Voice message sent")
    
    
# -------- SEND ATTACHMENT (DOCUMENT/FILE) --------
def send_attachment(contact, file_path):

    # 1. Bring WhatsApp to focus
    focus_whatsapp()
    time.sleep(1)

    # 2. Open chat (using your existing search logic)
    pyautogui.hotkey("ctrl", "f")
    time.sleep(1)

    pyautogui.hotkey("ctrl", "a")
    pyautogui.press("backspace")

    pyautogui.write(contact)
    time.sleep(2)

    pyautogui.press("down")
    pyautogui.press("enter")
    time.sleep(1)

    # 3. Click the "+" (Attach) button
    # ⚠️ CHANGE THESE COORDS: Hover over the "+" button next to the chat box
    pyautogui.moveTo(610, 963) 
    time.sleep(0.5)
    pyautogui.click()
    time.sleep(1)

    # 4. Click the "Document" option from the menu
    # ⚠️ CHANGE THESE COORDS: Hover over the "Document" button that pops up
    pyautogui.moveTo(539, 509) 
    time.sleep(0.5)
    pyautogui.click()
    time.sleep(2)

    # 5. Windows File Dialog opens (it automatically focuses on the file name box)
    # Write the absolute file path and hit Enter
    pyautogui.write(file_path, interval=0.02)
    time.sleep(1)
    pyautogui.press("enter")
    
    # 6. Wait for WhatsApp to load the file preview, then send!
    time.sleep(2) 
    pyautogui.press("enter")

    print(f"✅ Attachment '{file_path}' sent to {contact}")
   
   
# -------- SEND CONTACT CARD --------
def send_contact_card(target_person, contact_to_share):

    # 1. Bring WhatsApp to focus & open the target's chat
    focus_whatsapp()
    time.sleep(1)

    pyautogui.hotkey("ctrl", "f")
    time.sleep(1)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.press("backspace")
    pyautogui.write(target_person)
    time.sleep(2)
    pyautogui.press("down")
    pyautogui.press("enter")
    time.sleep(1)

    # 2. Click the "+" (Attach) button
    # ⚠️ Use your existing coordinates for the + button here
    pyautogui.moveTo(610, 963) 
    time.sleep(0.5)
    pyautogui.click()
    time.sleep(2)

    # 3. Click the "Contact" option from the menu
    # ⚠️ NEW COORDS NEEDED: Hover over the blue "Contact" icon in your screenshot!
    pyautogui.moveTo(591, 748) # <-- Change these!
    time.sleep(0.5)
    pyautogui.click()
    time.sleep(1.5)

    # 4. The "Search contacts" popup appears. Type the name.
    pyautogui.write(contact_to_share, interval=0.05)
    time.sleep(2) # Give it 2 full seconds to load the search results

    # 5. Press down to highlight them, and Enter to check the box
    pyautogui.press("down")
    time.sleep(0.5)
    pyautogui.press("enter") # This checks the green box
    time.sleep(1)

    # 6. Click the green Send arrow!
    # ⚠️ Put the new coordinates for the green arrow here!
    pyautogui.moveTo(1237, 912) 
    time.sleep(0.5)
    pyautogui.click()
    time.sleep(1.5)
    
    time.sleep(2.5)
    # 7. Click the SECOND green Send arrow (Final Confirmation!)
    # (Using the new coordinates you found)
    pyautogui.moveTo(1279, 818) 
    time.sleep(0.5)
    pyautogui.click()
    
    # Just the print statement, no speaking!
    print(f"✅ Contact card for '{contact_to_share}' sent to {target_person}")