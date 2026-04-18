from apps.notepad import *
from apps.calculator import *
from apps.word import *
from apps.powerpoint import *
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

import os
import re
# ... your other imports ...

import os

def get_desktop_path(folder_name="Desktop"):
    r"""
    Forces the path to the strict local C:\Users\<User>\... 
    Defaults to Desktop, but also supports Documents and Downloads.
    """
    user_profile = os.path.expanduser("~") 
    
    # Map the requested folder to the strict local path
    location_map = {
        "desktop": os.path.join(user_profile, "Desktop"),
        "documents": os.path.join(user_profile, "Documents"),
        "downloads": os.path.join(user_profile, "Downloads")
    }
    
    # Convert input to lowercase to prevent case-sensitivity errors
    folder_key = folder_name.lower()
    
    # Return the requested path (Defaults to Desktop if an unknown name is passed)
    return location_map.get(folder_key, location_map["desktop"])

# ==============================
# 🧠 ACTIVE APP DETECTION
# ==============================
def get_active_app():
    try:
        win = gw.getActiveWindow()
        if win and win.title:
            title = win.title.lower()
            if "notepad" in title:
                return "notepad"
            elif "whatsapp" in title:
                return "whatsapp"
            elif "word" in title:  # 🔥 NEW: Teach it to see Word!
                return "word"
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
    style=data.get("style") 
    color=data.get("color")     
    direction = data.get("direction")
    contact = data.get("contact")
    size = data.get("size")

    # ==============================
    # 📂 FILE SYSTEM (NEW)
    # ==============================
    if app == "file_system":
        intent = data.get("intent")
        entities = data.get("entities", {})

        # --- CREATE FOLDER LOGIC ---
        if intent == "create_folder":
            folder_name = entities.get("path", "New Folder")
            desktop_path = get_desktop_path() 
            final_path = os.path.join(desktop_path, folder_name)
                
            try:
                os.makedirs(final_path, exist_ok=True)
                print(f"✅ JARVIS: Folder '{folder_name}' created successfully at {final_path}")
            except Exception as e:
                print(f"❌ JARVIS: Could not create folder. Error: {e}")
            return True

        # 🔥 --- CREATE FILE LOGIC (NEW FIX) --- 🔥
        elif intent == "create_file":
            file_name = entities.get("path", "New_File.txt")
            
            # Smart Extension: Default to .txt if no extension was spoken
            if "." not in file_name:
                file_name += ".txt"
                
            desktop_path = get_desktop_path() 
            final_path = os.path.join(desktop_path, file_name)
                
            try:
                # This physically creates an empty file on the hard drive
                with open(final_path, 'w') as f:
                    pass 
                print(f"✅ JARVIS: File '{file_name}' created successfully at {final_path}")
            except Exception as e:
                print(f"❌ JARVIS: Could not create file. Error: {e}")
            return True

        # Call your professional file_service for anything else!
        result = handle_file_command(intent, entities)

        if result["status"] == "success":
            print(f"✅ JARVIS: {result['message']}")
            if intent == "search_file" and result.get("data"):
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
        
        elif action == "new_tab":
            new_tab()
        
        elif action == "delete":
            if line:
                delete_word_from_line(text, line)
            else:
                # 🔥 Make sure this matches the function name in notepad.py
                delete_word(text)
                
        # 🔥 ADD THIS NEW BLOCK RIGHT BELOW DELETE
        elif action == "delete_line":
            if line:
                # Ensure you import delete_specific_line at the top of main(brain).py!
                delete_specific_line(line) 

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
        elif action == "stop_voice":
            stop_voice_message()

        elif action == "send_attachment":
            contact = data.get("contact")
            spoken_file = data.get("file_name")
            location = data.get("location") # 🔥 Grab the location from NLP
            
            if contact and spoken_file:
                # Pass the location into your search tool!
                # real_file_path will now either be a single string path, or None (if cancelled/not found)
                real_file_path = find_document(spoken_file, specific_location=location)
                
                if real_file_path:
                    # Make sure se
                    # nd_attachment in whatsapp.py is ready to accept a full path
                    send_attachment(contact, real_file_path)
                else:
                    # It will print this if not found, OR if the user typed 'cancel'
                    if "cancel" not in str(real_file_path): 
                        print("🎙️ JARVIS SAYS: 'I could not find that file or the action was cancelled.'")
                    
        elif action == "send_contact_card":
            raw_target = data.get("target")
            raw_share_name = data.get("share_name")
            
            if raw_target and raw_share_name:
                # 📖 Translate BOTH nicknames into exact WhatsApp names!
                exact_target = resolve_contact(raw_target)
                exact_share_name = resolve_contact(raw_share_name)
                
                # Make sure send_contact_card is imported at the top of the file!
                send_contact_card(exact_target, exact_share_name)
                    
        elif action == "read_specific":
            # Ensure you import read_specific_message at the top of main!
            if contact:
                # Use your existing resolver to clean up the spoken name
                exact_name = resolve_contact(contact)
                read_specific_message(exact_name)
                
        elif action == "show_unread":
            show_unread_messages()
            
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
    # 📄 WORD
    # ==============================
    elif app == "word":
        if action == "open":
            open_word()
        elif action == "open_file":
            file_name = data.get("text")
            location = data.get("folder")
            
            # Use the smart search tool
            real_file_path = find_document(file_name, specific_location=location)
            
            if real_file_path:
                # Use os.startfile for a 100% portable launch
                os.startfile(real_file_path)
                print(f"✅ JARVIS: Opening {file_name}.")
            else:
                print(f"❌ JARVIS: Could not find '{file_name}' on this computer.")

        elif action == "close":
            close_word()
        elif action == "new":           
            new_document()
        elif action == "write":
            write_in_word(text)
        elif action == "save":
            folder = data.get("folder")
            
            save_word_file(text, folder)
        elif action == "style":
            apply_style(data.get("style"))
        elif action == "alignment":
            set_alignment(data.get("align"))
        elif action == "heading":
            apply_heading(data.get("level"))
        elif action == "style_specific":
            target = data.get("text")
            style = data.get("style")
            color = data.get("color")
            size = data.get("size")
            
            # Now passing all 4 pieces of data!
            style_specific_text(target, style, color, size)
            
        # --- ADVANCED NOTEPAD FEATURES PORTED TO WORD ---
        elif action == "read":
            read_word()
    
        elif action == "replace":
            old_word = data.get("old_text")
            new_word = data.get("new_text")
            if old_word and new_word:
                word_replace_word(old_word, new_word)
                
        elif action == "delete":
            word_delete_word(data.get("text"))
            
        elif action == "clear":
            word_clear()
            
        elif action == "insert":
            if line:
                word_insert_text_at_line(text, line)
            else:
                word_insert_at_cursor(text)
                
        elif action == "space":
            word_space()
            
        elif action == "new_line":
            word_new_line()
            
        elif action == "new_paragraph":
            word_new_paragraph()
            
        elif action == "move":
            word_move_cursor(direction)
            
        return True

    # ==============================
    # 📄 POWERPOINT
    # ==============================
    # Inside execute_action function:
    elif app == "powerpoint":
        if action == "open":
            open_powerpoint()
        elif action == "add_slide":
            add_slide()
        elif action == "start_slideshow": # 🔥 NEW CONNECTION
            start_slideshow()
        elif action == "delete_slide":
            # 🔥 Pass the slide number (text) to the function
            delete_slide(data.get("text"))
            
        elif action == "apply_theme":
            apply_presentation_theme(text)
        elif action == "stop_slideshow":
            stop_slideshow()    
        elif action == "navigate":
            # 🔥 FIX: You must actually call the function here!
            target = data.get("text")
            if target:
                navigate_slide(target)
        elif action == "set_title":
            # 🎯 Make sure we use data.get("text")
            msg = data.get("text") 
            if msg:
                set_slide_title(msg)
            else:
                print("⚠️ JARVIS: Found 'title' command but text was empty.")
        elif action == "set_subtitle": # 🔥 NEW CONNECTION
            set_slide_subtitle(data.get("text"))
        elif action == "set_content": # 🔥 NEW CONNECTION
            set_slide_content(data.get("text"))
        
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
            play_song(text) # text will be the playlist name from our query_map
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
# ✅ NLP RESULT VALIDATOR
# ==============================
def is_nlp_confident(data):
    action = data.get("action")
    intent = data.get("intent") # 🔥 Listen for File System intents

    # If BOTH are None, the NLP failed to understand the command
    if action is None and intent is None:
        # print("   🔍 DEBUG: Action/Intent is None. NLP is NOT confident. Sending to LLM...")
        return False
        
    return True

# ==============================
# 🚀 MAIN COMMAND PROCESSOR
# ==============================
import re

# 🔥 JARVIS'S MEMORY STATE
CURRENT_APP_STATE = "notepad" 

def process_command(command):
    global CURRENT_APP_STATE
    command = command.lower().strip()

    # 🔥 THE FIX: Don't split "and" if it's part of a styling command
    styling_keywords = ["color", "blue", "red", "green", "size", "bold", "italic"]
    if any(word in command for word in styling_keywords) and "and" in command:
        parts = [command] # Treat as one single command
    else:
        # 🔥 Add 'and' to the split logic so it handles multiple actions
        parts = re.split(r'\b(?:and then|and|then)\b', command)
    
    for part in parts:
        part = part.strip()
        if not part: continue
        
        # 1. Sync state with active window
        on_screen = get_active_app()
        if on_screen:
            CURRENT_APP_STATE = on_screen
            
        # 2. Try Local NLP
        nlp_data = process_nlp(part, CURRENT_APP_STATE) 
        # print("📊 NLP RESULT:", nlp_data)   
        
        # 3. Decision Logic
        confident = is_nlp_confident(nlp_data)
        
        if confident == True:
            if nlp_data.get("app"):
                CURRENT_APP_STATE = nlp_data["app"]
            execute_action(nlp_data, part)
            time.sleep(0.5)
# ==============================
# ▶️ RUN
# ==============================
if __name__ == "__main__":
    # print("🤖 JARVIS started...")
    

    while True:
        cmd = input("\nEnter command: ")

        if cmd.lower() == "exit":
            print("Exiting JARVIS...")
            break

        process_command(cmd)