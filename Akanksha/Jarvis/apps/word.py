import os
import time
import pyautogui
import pygetwindow as gw
from common import open_app_by_name, close_app
import win32com.client
import pyperclip

import pyttsx3
engine = pyttsx3.init()



# -------- FOCUS WORD --------
def focus_word():
    # Looks for any open window with "Word" in the title
    windows = gw.getWindowsWithTitle("Word")
    
    for win in windows:
        try:
            if win.isMinimized:
                win.restore()
            win.activate()
            time.sleep(0.5)
            return True
        except:
            continue
            
    return False

# -------- 1 & 2. OPEN / CLOSE --------
def open_word():
    # 1. 🔥 THE BOUNCER: Check if Word is already open first!
    if focus_word():
        print(" Word is already open. Brought to front!")
        return # <-- This 'return' completely stops the code from opening a duplicate!
        
    # 2. If it is NOT open, launch it
    print(" Opening Microsoft Word...")
    try:
        # This mirrors the 'Win + R -> winword' behavior perfectly
        os.startfile("winword") 
        
        # Give Word time to load the splash screen
        time.sleep(5) 
        
        # Press Enter to bypass the 'Blank Document' selection screen
        pyautogui.press('enter')
        print("✅ Word is ready.")
    except Exception as e:
        print(f"I encountered an error trying to bring Word to the front")

def close_word():
    """
    Universal Force-Close: Kills all Word processes.
    The /T flag ensures all 'child' windows are closed, and /F forces it.
    """
    print("Shutting down Microsoft Word...")
    
    # 🔥 THE PORTABLE WAY: Taskkill is much more reliable than close_app()
    # This hits 'WINWORD.EXE' directly.
    os.system("taskkill /f /im WINWORD.EXE /t >nul 2>&1")
    
    # print("✅ Word closed.")
        
# -------- 3. CREATE NEW DOCUMENT --------
def new_document():
    print(" Creating new document...")
    
    # 1. Try to bring Word to the front
    if focus_word():
        # If successful, press Ctrl + N
        pyautogui.hotkey('ctrl', 'n')
        # print("✅ Created a new blank document")
    else:
        # 2. If Word wasn't open at all, open it!
        # (Your open_word function already hits 'Enter' to make a blank doc)
        open_word()

# -------- 4. WRITE --------
def write_in_word(text):
    print("Writing")
    if focus_word():
        pyautogui.write(text, interval=0.01)
        # print(f"Typed in Word: {text}")
    else:
        print("Word is not open! Please open Word first.")



# -------- 5 & 6. SAVE (NAME & SPECIFIC FOLDER) --------
def save_word_file(file_name, folder_path=None):
    """
    Universal Save: Uses F12 to bypass the Word 'File' menu.
    """
    focus_word()
    time.sleep(0.5)

    # 1. Trigger 'Save As' Dialog
    pyautogui.press('f12')
    time.sleep(1.5) # Wait for dialog to open

    # 2. Construct the full path
    if folder_path:
        full_path = os.path.join(folder_path, file_name)
    else:
        # Default to Desktop if no folder was specified
        full_path = os.path.join(os.path.expanduser("~\\Desktop"), file_name)

    # 3. Type path and Save
    pyautogui.write(full_path, interval=0.05)
    time.sleep(0.5)
    pyautogui.press('enter')

    print(f"JARVIS: Document saved as '{file_name}'")

# -------- 8. ALIGNMENT (SMART ENGINE + VISUAL) --------
def set_alignment(align_type):
    """
    Portable Alignment: Uses Ctrl shortcuts.
    """
    focus_word()
    time.sleep(0.3)
    
    shortcuts = {
        "left": "l",
        "center": "e", # Note: 'e' for center
        "right": "r",
        "justify": "j"
    }
    
    if align_type in shortcuts:
        pyautogui.hotkey('ctrl', shortcuts[align_type])
        print(f" Text aligned to the {align_type}.")

# -------- 9. HEADINGS --------
def apply_heading(level):
    # print(f" Preparing to apply Heading {level}...")
    
    try:
        # 1. ATTEMPT TO CONNECT OR LAUNCH WORD
        try:
            word_app = win32com.client.GetActiveObject("Word.Application")
        except:
            print("📂 Word isn't open. Launching it via Engine...")
            word_app = win32com.client.Dispatch("Word.Application") 
            word_app.Visible = True
            word_app.Documents.Add() 
            time.sleep(2) 

        # 2. 🔥 FORCE TO FRONT SO YOU CAN SEE IT
        word_app.Activate()  
        focus_word()         
        
        # Give your eyes a second to adjust
        time.sleep(1.5)      

        # 3. APPLY HEADING VIA ENGINE
        selection = word_app.Selection
        
        # Word's internal API constants for styles:
        # -2 = Heading 1, -3 = Heading 2, -4 = Heading 3, etc.
        heading_constants = {1: -2, 2: -3, 3: -4, 4: -5, 5: -6}
        
        if level in heading_constants:
            selection.Style = heading_constants[level]
            print(f" Applied Heading {level}.")
        else:
            print(f" I can only do Headings 1 through 6.")
            
    except Exception as e:
        print(f"I encountered an error trying to bring Word to the front")
        # Manual Fallback just in case
        if focus_word():
            if 1 <= level <= 3:
                pyautogui.hotkey('ctrl', 'alt', str(level))
                print(f"✅ JARVIS: Applied Heading {level} via keyboard.")
        
# -------- 10. OPEN EXISTING FILE --------
def open_existing_word_file(file_path):
    if os.path.exists(file_path):
        # print(f"🚀 JARVIS: Opening document...")
        os.startfile(file_path)
        
        # Wait a few seconds for Word to launch the file
        time.sleep(4) 
        
        # Bring it to the front so you can start typing immediately
        focus_word()
        print("Here is your document")
    else:
        print(" File not found.")

# -------- 7. TEXT STYLING (HYBRID) --------
def apply_style(style_type):
    # print(f"🖌️ JARVIS: Attempting to {style_type} selection...")
    try:
        # METHOD A: The API (Invisible & Fast)
        word_app = win32com.client.GetActiveObject("Word.Application")
        sel = word_app.Selection
        if style_type == "bold": sel.Font.Bold = True
        elif style_type == "italic": sel.Font.Italic = True
        elif style_type == "underline": sel.Font.Underline = 1
        print(f"✅ Style applied ")
    except:
        # METHOD B: The Keyboard (Visual Backup)
        if focus_word():
            key = 'b' if style_type == "bold" else 'i' if style_type == "italic" else 'u'
            pyautogui.hotkey('ctrl', key)
            print(f"✅ Style applied ")


# Add this color dictionary right above your specific style function
word_colors = {
    "black": 1, "blue": 2, "green": 11, "pink": 5, 
    "purple": 12, "red": 6, "yellow": 7, "white": 8, "orange": 14
}

# -------- 11. STYLE SPECIFIC (SMART ENGINE) --------
def style_specific_text(target_text=None, style=None, color=None, size=None):
    focus_word()
    
    word_colors = {
        "black": 1, "blue": 2, "green": 11, "pink": 5, 
        "purple": 12, "red": 6, "yellow": 7, "white": 8, "orange": 14
    }

    try:
        # Connect to the running Word instance
        word_app = win32com.client.GetActiveObject("Word.Application")
        word_app.Visible = True # Ensure it's visible
        
        # We will work with the current selection/range
        if target_text:
            if isinstance(target_text, str): target_text = [target_text]
            
            for word in target_text:
                print(f"🎨 JARVIS: Searching for and formatting '{word}'...")
                
                # Start search from the beginning of the document
                find_obj = word_app.ActiveDocument.Content.Find
                find_obj.ClearFormatting()
                
                # 🔥 THE STABILIZER: Wrap=1 means search the entire document
                # Forward=True, MatchCase=False
                found = find_obj.Execute(word, False, False, False, False, False, True, 1)
                
                if found:
                    # Use the range of the found word
                    rng = find_obj.Parent 
                    
                    if style == "bold": rng.Font.Bold = True
                    if style == "italic": rng.Font.Italic = True
                    if style == "underline": rng.Font.Underline = 1
                    
                    if color and color.lower() in word_colors:
                        rng.Font.ColorIndex = word_colors[color.lower()]
                        
                    if size:
                        rng.Font.Size = size
                    
                    print(f" Successfully formatted '{word}'")
                else:
                    print(f" Could not find the word '{word}'")

        else:
            # If no specific word, apply to whatever is currently highlighted
            print(" Applying to current selection...")
            sel = word_app.Selection
            if style == "bold": sel.Font.Bold = True
            if style == "italic": sel.Font.Italic = True
            if style == "underline": sel.Font.Underline = 1
            if color and color.lower() in word_colors:
                sel.Font.ColorIndex = word_colors[color.lower()]
            if size:
                sel.Font.Size = size

    except Exception as e:
        print(f"I encountered an error communicating with Word. Please make sure the document is open and active")
        
# ==========================================
# 🧠 ADVANCED WORD FEATURES (From Notepad)
# ==========================================

# -------- READ ALOUD --------
def read_word():
    # 🔥 FORCE TO FRONT
    if not focus_word():
        print("Word is not open.")
        return

    print("Reading Word document...")
    try:
        word_app = win32com.client.GetActiveObject("Word.Application")
        # 🔥 SECOND FORCE (API level)
        word_app.Activate() 
        
        text = word_app.ActiveDocument.Content.Text
        clean_text = text.replace('\r', '\n').strip()
        
        if not clean_text:
            print(" The document is completely empty.")
            return

        # 2. 🔥 THE OUTPUT FIX: Print the text beautifully to the terminal
        print(clean_text)
      
    except Exception as e:
        print(f"I encountered an error while trying to read the Word document")

# -------- REPLACE WORD --------
def word_replace_word(old_word, new_word):
    # 🔥 FORCE TO FRONT
    focus_word() 

    print(f"Replacing '{old_word}' with '{new_word}' in Word")
    try:
        word_app = win32com.client.GetActiveObject("Word.Application")
        word_app.Activate() # 🔥 Bring to front via API
        
        find_obj = word_app.ActiveDocument.Content.Find
        find_obj.Execute(old_word, False, False, False, False, False, True, 1, False, new_word, 2)
        print(f"✅ JARVIS: Replaced '{old_word}' with '{new_word}'.")
    except Exception as e:
        print(f"I encountered an error while trying to replace that text.")

# -------- DELETE WORD --------
def word_delete_word(word_to_delete):
    focus_word() 
    # Deleting is just replacing with nothing!
    word_replace_word(word_to_delete, "")

# -------- CLEAR DOCUMENT --------
def word_clear():
    # 🔥 FORCE TO FRONT
    focus_word() 

    print("Clearing Word document...")
    try:
        word_app = win32com.client.GetActiveObject("Word.Application")
        word_app.Activate()
        word_app.ActiveDocument.Content.Delete()
        print("✅ JARVIS: Word document cleared.")
    except Exception as e:
        print(f"I encountered an error while trying to clear the document")
        
# -------- LINE / PARAGRAPH INSERTION --------
def word_insert_text_at_line(text, line_number):
    # 🔥 FORCE TO FRONT
    focus_word() 

    try:
        word_app = win32com.client.GetActiveObject("Word.Application")
        word_app.Activate()
        doc = word_app.ActiveDocument
        paragraphs = doc.Paragraphs
        
        if 0 < line_number <= paragraphs.Count:
            rng = paragraphs(line_number).Range
            rng.InsertBefore(text + " ")
            print(f" Inserted text at paragraph {line_number}.")
        elif line_number == paragraphs.Count + 1:
            doc.Content.InsertAfter("\n" + text)
            print(f" Appended text.")
    except Exception as e:
         print(f"I encountered an error while trying to insert the text")

# -------- CURSOR MOVEMENTS & SPACING --------
def word_space():
    print("Pressing space")
    if focus_word(): pyautogui.press('space')

def word_new_line():
    print("Going to new line")
    if focus_word(): pyautogui.press('enter')

def word_new_paragraph():
    print("Going to new paragraph")
    if focus_word():
        pyautogui.press('enter')
        pyautogui.press('enter')

def word_move_cursor(direction):
    print(f"moving {direction}")
    if focus_word(): pyautogui.press(direction)

def word_insert_at_cursor(text):
    if focus_word():
        pyperclip.copy(text)
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'v')