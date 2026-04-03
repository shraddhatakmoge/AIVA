from apps.notepad import *
from apps.calculator import *
from apps.vscode import open_vscode, close_vscode
from apps.word import open_word, close_word
from apps.powerpoint import open_powerpoint, close_powerpoint
from apps.spotify import *
from apps.whatsapp import *
from common import find_document, resolve_contact
from nlp import process_nlp
from services.file_service import handle_file_command

import pygetwindow as gw
import time
import pyautogui

pyautogui.FAILSAFE = False


def toggle_mic():
    pyautogui.hotkey("win", "alt", "k")


# ==============================
# 🧠 ACTIVE APP DETECTION
# ==============================
def get_active_app():
    try:
        win = gw.getActiveWindow()
        if win and win.title:
            title = win.title.lower()
            # Checks if "notepad" exists anywhere in the title
            if "notepad" in title:
                return "notepad"
            elif "whatsapp" in title:
                return "whatsapp"
    except Exception as e:
        print(f"⚠️ Window detection error: {e}")
    return None

# ==============================
# ⚙️ EXECUTE ACTION (shared by NLP + LLM)
# ==============================
def execute_action(data, original_command=""):
    """
    Takes a parsed data dict and runs the correct app function.
    """
    app = data.get("app")
    action = data.get("action")
    text = data.get("text")
    line = data.get("line")
    direction = data.get("direction")
    contact = data.get("contact")

    # ==============================
    # 📂 FILE SYSTEM (NEW)
    # ==============================
    if app == "file_system":
        intent = data.get("intent")
        entities = data.get("entities")

        # Call your professional file_service!
        result = handle_file_command(intent, entities)

        if result["status"] == "success":
            print(f"✅ JARVIS: {result['message']}")
            if intent == "search_file" and result["data"]:
                print("Found matches:")
                for path in result["data"]:
                    print(f" - {path}")
        else:
            print(f"❌ JARVIS: {result['message']}")

        return True

    # ==============================
    # 📝 NOTEPAD
    # ==============================
    if app == "notepad":
        # 🔥 CRITICAL: Always focus Notepad before doing anything
        win = focus_notepad() 
        if not win:
            print("❌ Notepad could not be found or opened.")
            return

        if action == "open":
            open_notepad()
            
        elif action == "write":
            write_text(text)
            
        elif action == "space":
            press_space()

        elif action == "move":
            move_cursor(direction)

        elif action == "new_line":
            new_line()

        elif action == "new_paragraph":
            new_paragraph()
            
        elif action == "undo":
            undo_action()
        
        elif action == "redo":
            redo_action()
            
        elif action == "clear":
            clear_notepad()
        
        elif action == "delete":
            if line:
                delete_word_from_line(text, line)
            else:
                delete_word(text)

        elif action == "read":
            # 1. Try to find any window with "Notepad" in the title
            try:
                notepad_windows = gw.getWindowsWithTitle('Notepad')
                if notepad_windows:
                    # Bring the first Notepad window found to the front
                    notepad_win = notepad_windows[0]
                    notepad_win.activate()
                    time.sleep(0.5) # Wait for Windows to switch focus
            except Exception as e:
                print(f"⚠️ Could not focus Notepad: {e}")

            # 2. Now check if it successfully became active
            active_app = get_active_app()
            if active_app == "notepad":
                read_notepad()
            else:
                print("❌ Notepad not active. Please click the Notepad window first!")
                
        elif action == "save":
            # If the NLP found a filename, use it. Otherwise, default to test.txt
            filename_to_use = text if text else "test.txt"
            save_file(filename_to_use)
            
        elif action == "replace":
            old_word = data.get("old_text")
            new_word = data.get("new_text")
            
            if old_word and new_word:
                # This calls the fast clipboard function we just wrote in notepad.py!
                replace_word(old_word, new_word)
            
        elif action == "new":
            active_app = get_active_app()
            if active_app == "notepad":
                pyautogui.hotkey('ctrl', 'n')
            else:
                open_notepad()
                
        elif action == "insert":
            if line:
                insert_text_at_line(text, line)
            else:
                insert_at_cursor(text)
                
                

        elif action == "close":
            close_notepad()

        return True

    # ==============================
    # 💬 WHATSAPP
    # ==============================
    elif app == "whatsapp":

        if action == "open":
            open_whatsapp()

        elif action == "close":
            close_whatsapp()

        elif action == "send":
            if text:
                send_message(text)

        elif action == "send_to":
            if contact and text:
                send_message_to(contact, text)

        elif action == "screenshot":
            if contact:
                send_screenshot(contact)

        elif action == "voice_call":
            voice_call(contact)

        elif action == "video_call":
            video_call(contact)

        elif action == "open_status":
            open_status_by_click(contact)

        elif action == "voice_note":
            send_voice_message(contact)

        # In main(brain).py under the WhatsApp section:
        elif action == "send_attachment":
            contact = data.get("contact")
            spoken_file = data.get("file_name")
            location = data.get("location") # 🔥 Grab the location from NLP
            
            if contact and spoken_file:
                # Pass the location into your search tool!
                real_file_path = find_document(spoken_file, specific_location=location)
                
                if real_file_path:
                    send_attachment(contact, real_file_path)
                else:
                    print("🎙️ JARVIS SAYS: 'I could not find that file on your computer.'")
                    
        elif action == "send_contact_card":
            raw_target = data.get("target")
            raw_share_name = data.get("share_name")
            
            if raw_target and raw_share_name:
                # 📖 Translate BOTH nicknames into exact WhatsApp names!
                exact_target = resolve_contact(raw_target)
                exact_share_name = resolve_contact(raw_share_name)
                
                # Make sure send_contact_card is imported at the top of the file!
                send_contact_card(exact_target, exact_share_name)
                    

        return True

    # ==============================
    # 🖩 CALCULATOR
    # ==============================
    elif app == "calculator":

        from apps.calculator import open_calculator, close_calculator, calculate

        if action == "open":
            open_calculator()
            return True

        elif action == "close":
            close_calculator()
            return True

        elif action == "calculate":
            calculate(original_command, data.get("expression")) 
            return True
          

    # ==============================
    # 💻 VS CODE
    # ==============================
    elif app == "vscode":
        if action == "open":
            open_vscode()
        elif action == "close":
            close_vscode()
        return True

    # ==============================
    # 📄 WORD
    # ==============================
    elif app == "word":
        if action == "open":
            open_word()
        elif action == "close":
            close_word()
        return True

    # ==============================
    # 📊 POWERPOINT
    # ==============================
    elif app == "powerpoint":
        if action == "open":
            open_powerpoint()
        elif action == "close":
            close_powerpoint()
        return True

    # ==============================
    # 🎵 SPOTIFY
    # ==============================
    elif app == "spotify":

        # 🔥 Make sure open_spotify is imported here!
        from apps.spotify import (
            open_spotify,
            close_spotify,
            play_song,
            pause_music,
            resume_music,
            next_track,
            previous_track,
            like_song
        )   

        # 🔥 ADD THIS NEW BLOCK:
        # "
        if action == "open":
            open_spotify()
            return True

        elif action == "close":
            close_spotify()
            return True
        
        elif action == "play":
            play_song(text)
            return True

        elif action == "pause":
            pause_music()
            return True

        elif action == "resume":
            resume_music()
            return True

        elif action == "next":
            next_track()
            return True

        elif action == "previous":
            previous_track()
            return True

        elif action == "like":
            like_song()
            return True
    

    # ==============================
    # ⚙️ SYSTEM
    # ==============================
    elif app == "system":
        if action in ("mute_mic", "unmute_mic"):
            toggle_mic()
        return True

    return False  # nothing matched


# ==============================
# ✅ NLP RESULT VALIDATOR
# ==============================
def is_nlp_confident(data):
    """
    Returns True only if NLP produced a meaningful result.
    If app is defaulted to 'notepad' with no clear action, it's not confident.
    """
    app = data.get("app")
    action = data.get("action")

    # NLP defaults app to 'notepad' when nothing matches — that's a weak result
    if app == "notepad" and action is None:
        return False

    # No app and no action = NLP found nothing useful
    if app is None and action is None:
        return False

    return True


# ==============================
# 🚀 MAIN COMMAND PROCESSOR
# ==============================
import re

def process_command(command):
    # Standardize input
    command = command.lower().strip()

    # 1. Global Commands
    if command == "stop":
        from apps.whatsapp import stop_voice_message
        stop_voice_message()
        return

    # 2. Split the sentence into multiple parts
    parts = re.split(r'\b(?:and then|then|and)\b', command)
    
    for part in parts:
        part = part.strip().strip(',').strip('.') 
        if not part: continue
        
        print(f"🤖 JARVIS processing: {part}")

        # --- THIS IS THE MISSING STEP ---
        # 3. Analyze THIS specific part of the sentence
        nlp_data = process_nlp(part) 
        
        # 4. Contextual Check
        # If no app was found, but Notepad is active, assume Notepad
        if nlp_data.get("app") is None:
            active = get_active_app()
            if active == "notepad":
                nlp_data["app"] = "notepad"

        # 5. Validate and Execute
        if is_nlp_confident(nlp_data):
            execute_action(nlp_data, part)
            # Prevent text from "smushing" together
            time.sleep(0.3) 
        else:
            print(f"❌ JARVIS: I couldn't understand '{part}'")
# ==============================
# ▶️ RUN
# ==============================
if __name__ == "__main__":
    print("🤖 JARVIS started...")
    

    while True:
        cmd = input("\nEnter command: ")

        if cmd.lower() == "exit":
            print("Exiting JARVIS...")
            break

        process_command(cmd)