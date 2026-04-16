import os
import time
import pyautogui
import pygetwindow as gw
import pyperclip
import pyttsx3



pyautogui.FAILSAFE = False

last_message = ""
engine = pyttsx3.init()
STOP_RECORDING = False  

# -------- OPEN --------
def open_whatsapp():
    print("Opening Whatsapp for you")
    
    # 1. Build the dynamic paths where the .exe is typically installed
    local_appdata = os.environ.get("LOCALAPPDATA", "")
    program_files = os.environ.get("PROGRAMFILES", "")
    
    exe_path_local = os.path.join(local_appdata, "WhatsApp", "WhatsApp.exe")
    exe_path_prog = os.path.join(program_files, "WhatsApp", "WhatsApp.exe")
    
    # 2. Check for the .exe version first
    if os.path.exists(exe_path_local):
        os.startfile(exe_path_local)
        
    elif os.path.exists(exe_path_prog):
        os.startfile(exe_path_prog)
        
    else:
        # 3. Fallback to your original Microsoft Store App version
        os.system("start shell:AppsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App")
        
    time.sleep(3)


# -------- CLOSE --------
def close_whatsapp():
    print("Closing Whatsapp")


    # Try process kill
    os.system("taskkill /f /im WhatsApp.exe >nul 2>&1")

    # Fallback: close by window title
    os.system('taskkill /f /fi "WINDOWTITLE eq WhatsApp*" >nul 2>&1')

    # print("✅ WhatsApp closed")

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
    print("Sending message")
    global last_message

    focus_whatsapp()
    time.sleep(1)

    pyautogui.write(text, interval=0.05)
    pyautogui.press("enter")

    last_message = text
    # print("📤 Sent:", text)


# -------- SEND TO CONTACT --------
def send_message_to(contact, text):
    global last_message
    
    # Keeping your preference: eventually swap this print for your engine.speak()
    print(f"Sending message to {contact}") 
    
    # 1. Guarantee Focus
    focus_whatsapp()
    time.sleep(2) # Extra buffer for the UI to completely settle

    # 2. Open Search
    pyautogui.hotkey("ctrl", "f")
    time.sleep(1.5) # WhatsApp search animations can be laggy
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.2)
    pyautogui.press("backspace")
    time.sleep(0.3)


    # 3. Type Contact Name
    pyautogui.write(contact)
    time.sleep(2.5) # 🔥 CRITICAL: Wait for the network to fetch the contact list

    # 4. Select Contact and Open Chat
    pyautogui.press("down")
    time.sleep(0.2)
    pyautogui.press("enter")
    time.sleep(1.5) # Wait for the chat screen to slide in

    # 5. Type Message and Send
    pyautogui.write(text, interval=0.02)
    time.sleep(0.5)
    pyautogui.press("enter")

    last_message = text

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

    # 🔥 SMART SCREENSHOT PATH FIX (Portable across different PCs)
    user_profile = os.path.expanduser('~')
    
    # Check OneDrive first (since your PC uses it), then the standard local path
    paths_to_check = [
        os.path.join(user_profile, "OneDrive", "Pictures", "Screenshots"),
        os.path.join(user_profile, "Pictures", "Screenshots")
    ]
    
    folder = None
    for p in paths_to_check:
        if os.path.exists(p):
            folder = p
            break

    if not folder:
        print(" Could not find the Screenshots folder on this PC.")
        return

    path = get_latest_screenshot(folder)

    if not path:
        print(f" No screenshots found in {folder}")
        return

    # print("📸 Sending:", path)

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
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.2)
    pyautogui.press("backspace")
    time.sleep(0.3)

    pyautogui.write(contact)
    time.sleep(2)

    pyautogui.press("down")
    pyautogui.press("enter")
    time.sleep(1)

    # 🔥 Step 5: Paste image
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1)

    pyautogui.press("enter")
    pyautogui.press("enter")

    print(f"Latest screenshot sent to {contact}")

# --------- VOICE CALL ---------
def voice_call(contact):
    print(f"Voice calling {contact}")
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

    for _ in range(7):
        pyautogui.press("tab")
        time.sleep(0.2)

    pyautogui.press("enter")
    


    # print("🎥 Video calling", contact)

# ------ VIDEO CALL -------    
def video_call(contact):
    print(f"Video calling {contact}")
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
    
    # print("🎥 Video calling", contact)
    
        
# ---------- CHECK STATUS ---------      
def open_status_by_click(contact):
    print(f"Opening status of {contact}")

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
    pyautogui.moveTo(157, 445)  # 👈 replace with your coords
    time.sleep(0.5)
    pyautogui.click()

    # print("👁️ Status opened")
    

# -------- VOICE MESSAGE -----------
def send_voice_message(contact):
    open_whatsapp()
    # No need for threads anymore! It runs, locks the mic, and finishes.
    _record_voice(contact)

def _record_voice(contact):
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

    print(f"➡️ Chat opened for {contact}")

    # 🎤 Move to Mic
    pyautogui.moveTo(1848, 955)
    time.sleep(0.5)

    # 🔥 THE FIX: Swipe UP to lock the mic
    pyautogui.mouseDown()
    time.sleep(0.5)
    pyautogui.moveRel(0, -100, duration=0.5) # Drags the mouse up 100 pixels
    pyautogui.mouseUp()                      # Releases the mouse. Mic is now locked!

    print("🎙️ Recording Locked... (Type 'stop recording' when ready to send)")

    
def stop_voice_message():
    # 🔥 Bring WhatsApp to front
    focus_whatsapp()
    time.sleep(1)

    # 🎯 Move back to the exact same coordinates (which is now the SEND button)
    pyautogui.moveTo(1848, 955)  
    time.sleep(0.3)

    # 🔥 Click to send
    pyautogui.click()

    print("✅ Voice message sent")
    
# -------- SEND ATTACHMENT (DOCUMENT/FILE) --------
def send_attachment(contact, filename, search_location=None):
    """
    Portable version: Now supports both simple filenames and full paths.
    """
    # --- STEP 1: DYNAMIC PATH RESOLUTION ---
    
    # 🔥 THE FIX: If 'filename' is already a full path, use it directly!
    if os.path.isabs(filename) and os.path.exists(filename):
        file_path = filename
    else:
        # Otherwise, perform the search logic we built earlier
        user_home = os.path.expanduser("~")
        location_map = {
            "desktop": os.path.join(user_home, "Desktop"),
            "downloads": os.path.join(user_home, "Downloads"),
            "documents": os.path.join(user_home, "Documents")
        }
        
        file_path = None
        
        # Priority search for local desktop (where you create files)
        local_desktop = location_map["desktop"]
        
        # Check if the file (with or without .txt) exists there
        for ext in ["", ".txt", ".docx", ".pdf"]:
            temp_name = filename + ext
            temp_path = os.path.join(local_desktop, temp_name)
            if os.path.exists(temp_path):
                file_path = temp_path
                break

    if not file_path:
        print(f"Could not find '{filename}' on Desktop or other folders.")
        return

    # --- STEP 2: PORTABLE UI NAVIGATION ---
    # print(f"📎 JARVIS: Path verified: {file_path}")
    focus_whatsapp()

    # Universal Search shortcut
    pyautogui.hotkey("ctrl", "f")
    time.sleep(0.5)
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.3)
    pyautogui.press("backspace")
    time.sleep(0.3)
    pyautogui.write(contact)
    time.sleep(1.5)
    pyautogui.press("enter")
    time.sleep(1)

    
    # Navigation to '+' button
    pyautogui.hotkey("shift", "tab")
    pyautogui.hotkey("shift", "tab")
    time.sleep(0.3)
    pyautogui.press("enter") 
    time.sleep(1)

    # Select 'Document'
    pyautogui.press("enter") 
    time.sleep(2)

    # Standard Windows File Dialog
    pyautogui.write(file_path)
    time.sleep(0.5)
    pyautogui.press("enter")
    
    # --- PREVIEW & SEND ---
    time.sleep(4) 
    
    focus_whatsapp() 
    time.sleep(0.5)
    pyautogui.press("tab")
    time.sleep(0.3)
    pyautogui.press("enter")
    
    print(f"Document sent to {contact}")
    
   
   
   
# -------- SEND CONTACT CARD --------
def send_contact_card(target_person, contact_to_share):
    """
    Portable version: Uses keyboard navigation instead of coordinates 
    to ensure it works on any screen resolution.
    """
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
    time.sleep(1.5)

    # 2. Open Attachment Menu using keyboard
    # From the message box, Shift+Tab twice usually lands on the '+' button
    pyautogui.hotkey("shift", "tab")
    pyautogui.hotkey("shift", "tab")
    time.sleep(0.5)
    pyautogui.press("enter") 
    time.sleep(1.5)

    # 3. Navigate to "Contact" in the menu
    # Usually, 'Contact' is the 4th item down in the attachment menu
    for _ in range(4):
        pyautogui.press("down")
        time.sleep(0.1)
    pyautogui.press("enter")
    time.sleep(2)

    # 4. Search and Select the contact card
    pyautogui.write(contact_to_share, interval=0.05)
    time.sleep(2.5) # Wait for search results to populate

    pyautogui.press("down")
    time.sleep(0.3)
    pyautogui.press("enter") # Checks the box for the contact
    time.sleep(1)

    # 5. Final Send Sequence
    # Tab to jump from the search box to the 'Send' arrow
    # Usually 2-3 tabs are needed to reach the final green arrow
    for _ in range(3):
        pyautogui.press("tab")
        time.sleep(0.5)
        pyautogui.press("enter")
        
    pyautogui.press("tab")
    pyautogui.press("tab")
    pyautogui.press("enter")
    
    print(f"✅ Contact card for '{contact_to_share}' sent to {target_person}")
    
# -------- READ LATEST MESSAGE FROM SPECIFIC PERSON --------
def read_specific_message(contact):
    print(f" Retrieving latest messages from {contact}...")
    focus_whatsapp()
    time.sleep(1)

    # 1. Clear UI state
    for _ in range(3):
        pyautogui.press("esc")
        time.sleep(0.3)

    # 2. Search for the exact person
    pyautogui.hotkey("ctrl", "f")
    time.sleep(0.5)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.press("backspace")
    pyautogui.write(contact, interval=0.05)
    time.sleep(2.5) # Wait for search results to load

    # 3. Open their chat
    pyautogui.press("down")
    time.sleep(0.2)
    pyautogui.press("enter")
    time.sleep(1.5) # Wait for chat to open

    # 4. Copy the messages using a Loop!
    all_messages = []
    
    # Jump backwards 3 times to safely reach the message history
    for _ in range(3):
        pyautogui.hotkey("shift", "tab") 
        time.sleep(0.2)
    
    # 🔥 THE LOOP FIX: Try to read up to 5 messages in a row
    for _ in range(5):
        pyperclip.copy("EMPTY_MARKER")
        
        # Your custom UI bypass logic to copy ONE message
        pyautogui.press("right")
        pyautogui.press("enter")
        pyautogui.press("down")
        pyautogui.press("enter")
        time.sleep(0.3)
        
        current_msg = pyperclip.paste()
        
        # If nothing copied, or we are copying the exact same message again, stop the loop!
        if current_msg == "EMPTY_MARKER" or current_msg in all_messages:
            break
            
        # Save the message to our list
        all_messages.append(current_msg)
        
        # Press Down to move the highlight to the next message bubble!
        pyautogui.press("down")
        time.sleep(0.2)

    # Combine all the messages we collected into one clean paragraph
    text = "\n".join(all_messages)

    # 5. Output the result
    if not all_messages:
        print(f"Could not read a message from {contact}.")
        # speak(f"Could not read a message from {contact}.")
        return

    # 🔥 THE CLEAN PRINT FIX
    print(f"\n Messages from {contact} is")
    # print("--------------------------------------------------")
    print(text)
    # print("--------------------------------------------------\n")
  
    
    # Return focus to the typing box to reset the UI state
    for _ in range(3):
        pyautogui.press("tab")
        time.sleep(0.1)

# ------ SHOW UNREAD MESSAGES (FILTER ONLY) --------

def show_unread_messages():
    print("Here are your unread messages")
    focus_whatsapp()
    time.sleep(1)

    # 1. Clear any active search or open chat
    for _ in range(3):
        pyautogui.press("esc")
        time.sleep(0.3)
    
    # 2. Toggle the Unread Filter ON
    pyautogui.hotkey("ctrl", "f")  # Jump to Search Box
    time.sleep(0.5)
    pyautogui.press("tab")         # Tab over to the 'Unread Filter' icon next to it
    pyautogui.press("right") 
    time.sleep(0.2)
    pyautogui.press("enter")       # Toggle the filter ON