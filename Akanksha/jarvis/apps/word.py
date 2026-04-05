import os
import time
import pyautogui
import pygetwindow as gw
from common import open_app_by_name, close_app
import win32com.client
import pyperclip

import pyttsx3
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()




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
        print("✅ JARVIS: Word is already open. Brought to front!")
        return # <-- This 'return' completely stops the code from opening a duplicate!
        
    # 2. If it is NOT open, launch it
    print("🚀 JARVIS: Opening Microsoft Word...")
    try:
        # This mirrors the 'Win + R -> winword' behavior perfectly
        os.startfile("winword") 
        
        # Give Word time to load the splash screen
        time.sleep(5) 
        
        # Press Enter to bypass the 'Blank Document' selection screen
        pyautogui.press('enter')
        print("✅ Word is ready.")
    except Exception as e:
        print(f"❌ Error opening Word: {e}")

def close_word():
    print("❌ Closing Word...")
    # Use the process name found in Task Manager for Word
    close_app("WINWORD.EXE")
        
# -------- 3. CREATE NEW DOCUMENT --------
def new_document():
    print("🚀 JARVIS: Creating new document...")
    
    # 1. Try to bring Word to the front
    if focus_word():
        # If successful, press Ctrl + N
        pyautogui.hotkey('ctrl', 'n')
        print("✅ Created a new blank document")
    else:
        # 2. If Word wasn't open at all, open it!
        # (Your open_word function already hits 'Enter' to make a blank doc)
        open_word()

# -------- 4. WRITE --------
def write_in_word(text):
    if focus_word():
        pyautogui.write(text, interval=0.01)
        print(f"✅ Typed in Word: {text}")
    else:
        print("❌ Word is not open! Please open Word first.")

# -------- 5 & 6. SAVE (NAME & SPECIFIC FOLDER) --------
def save_word_file(filename, folder_path=None):
    if focus_word():
        print("💾 JARVIS: Opening Save dialog...")
        
        pyautogui.press('f12')
        time.sleep(2.5) # Wait for the window
        
        # 🔥 CLEAR THE BOX FIRST
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.press('backspace')
        time.sleep(0.2)
        
        if folder_path:
            # Type the absolute path so Windows knows EXACTLY where to put it
            full_path = os.path.join(folder_path, filename)
            pyautogui.write(full_path, interval=0.02)
        else:
            pyautogui.write(filename, interval=0.02)
            
        time.sleep(0.5)
        pyautogui.press('enter')
        print(f"✅ Document saved to: {folder_path if folder_path else 'Default Folder'} as {filename}")
    else:
        print("❌ Word is not open! Cannot save.")

# -------- 8. ALIGNMENT (SMART ENGINE + VISUAL) --------
def set_alignment(align):
    print(f"📐 JARVIS: Preparing to align text to the {align}...")
    
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
        
        # Give your eyes a second to adjust to the screen
        time.sleep(1.5)      

        # 3. APPLY ALIGNMENT VIA ENGINE
        selection = word_app.Selection
        
        # Word API Alignment values: 0 = Left, 1 = Center, 2 = Right, 3 = Justify
        if align == "left":
            selection.ParagraphFormat.Alignment = 0
        elif align == "center":
            selection.ParagraphFormat.Alignment = 1
        elif align == "right":
            selection.ParagraphFormat.Alignment = 2
        elif align == "justify":
            selection.ParagraphFormat.Alignment = 3
            
        print(f"✅ JARVIS: Text aligned {align}.")
        
    except Exception as e:
        print(f"⚠️ API Failed, trying manual shortcut... Error: {e}")
        # Manual Fallback just in case
        if focus_word():
            if align == "left": pyautogui.hotkey('ctrl', 'l')
            elif align == "center": pyautogui.hotkey('ctrl', 'e')
            elif align == "right": pyautogui.hotkey('ctrl', 'r')
            elif align == "justify": pyautogui.hotkey('ctrl', 'j')

# -------- 9. HEADINGS --------
def apply_heading(level):
    print(f"🏷️ JARVIS: Preparing to apply Heading {level}...")
    
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
            print(f"✅ JARVIS: Applied Heading {level}.")
        else:
            print(f"❌ JARVIS: I can only do Headings 1 through 6.")
            
    except Exception as e:
        print(f"⚠️ API Failed, trying manual shortcut... Error: {e}")
        # Manual Fallback just in case
        if focus_word():
            if 1 <= level <= 3:
                pyautogui.hotkey('ctrl', 'alt', str(level))
                print(f"✅ JARVIS: Applied Heading {level} via keyboard.")
        
# -------- 10. OPEN EXISTING FILE --------
def open_existing_word_file(file_path):
    if os.path.exists(file_path):
        print(f"🚀 JARVIS: Opening document...")
        os.startfile(file_path)
        
        # Wait a few seconds for Word to launch the file
        time.sleep(4) 
        
        # Bring it to the front so you can start typing immediately
        focus_word()
        print("✅ Document opened and ready.")
    else:
        print("❌ File not found.")

# -------- 7. TEXT STYLING (HYBRID) --------
def apply_style(style_type):
    print(f"🖌️ JARVIS: Attempting to {style_type} selection...")
    try:
        # METHOD A: The API (Invisible & Fast)
        word_app = win32com.client.GetActiveObject("Word.Application")
        sel = word_app.Selection
        if style_type == "bold": sel.Font.Bold = True
        elif style_type == "italic": sel.Font.Italic = True
        elif style_type == "underline": sel.Font.Underline = 1
        print(f"✅ Style applied via API.")
    except:
        # METHOD B: The Keyboard (Visual Backup)
        if focus_word():
            key = 'b' if style_type == "bold" else 'i' if style_type == "italic" else 'u'
            pyautogui.hotkey('ctrl', key)
            print(f"✅ Style applied via Keyboard.")

import keyboard

# Add this color dictionary right above your specific style function
word_colors = {
    "black": 1, "blue": 2, "green": 11, "pink": 5, 
    "purple": 12, "red": 6, "yellow": 7, "white": 8, "orange": 14
}

# -------- 11. STYLE SPECIFIC (SMART ENGINE) --------
def style_specific_text(target_text, style_type=None, color_name=None, font_size=None):
    print(f"🚀 JARVIS: Preparing to style '{target_text}'...")
    
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

        # 2. BRING TO FRONT
        focus_word()
        doc = word_app.ActiveDocument
        
        # 3. THE ENGINE SEARCH
        search_range = doc.Content
        find = search_range.Find
        find.ClearFormatting()
        find.Text = target_text
        
        # 4. EXECUTE & APPLY ALL STYLES
        if find.Execute():
            # Apply Bold/Italic/Underline
            if style_type == "bold": search_range.Font.Bold = True
            elif style_type == "italic": search_range.Font.Italic = True
            elif style_type == "underline": search_range.Font.Underline = 1
            
            # Apply Color
            if color_name and color_name in word_colors:
                search_range.Font.ColorIndex = word_colors[color_name]
                
            # Apply Size
            if font_size:
                search_range.Font.Size = font_size
            
            print(f"✅ JARVIS: Styled '{target_text}' successfully.")
        else:
            print(f"❌ JARVIS: I couldn't find the word '{target_text}' on the page.")

    except Exception as e:
        print(f"❌ Error in Master Style Function: {e}")
        
# ==========================================
# 🧠 ADVANCED WORD FEATURES (From Notepad)
# ==========================================

# -------- READ ALOUD --------
def read_word():
    # 🔥 FORCE TO FRONT
    if not focus_word():
        print("❌ Word is not open.")
        return

    print("🔊 JARVIS: Reading Word document...")
    try:
        word_app = win32com.client.GetActiveObject("Word.Application")
        # 🔥 SECOND FORCE (API level)
        word_app.Activate() 
        
        text = word_app.ActiveDocument.Content.Text
        clean_text = text.replace('\r', '\n').strip()
        
        if not clean_text:
            speak("There is no text.")
            return

        speak(clean_text)
    except Exception as e:
        print(f"❌ Error: {e}")

# -------- REPLACE WORD --------
def word_replace_word(old_word, new_word):
    # 🔥 FORCE TO FRONT
    focus_word() 

    print(f"🔄 JARVIS: Replacing '{old_word}' with '{new_word}' in Word...")
    try:
        word_app = win32com.client.GetActiveObject("Word.Application")
        word_app.Activate() # 🔥 Bring to front via API
        
        find_obj = word_app.ActiveDocument.Content.Find
        find_obj.Execute(old_word, False, False, False, False, False, True, 1, False, new_word, 2)
        print(f"✅ JARVIS: Replaced '{old_word}' with '{new_word}'.")
    except Exception as e:
        print(f"❌ Error: {e}")

# -------- DELETE WORD --------
def word_delete_word(word_to_delete):
    focus_word() 
    # Deleting is just replacing with nothing!
    word_replace_word(word_to_delete, "")

# -------- CLEAR DOCUMENT --------
def word_clear():
    # 🔥 FORCE TO FRONT
    focus_word() 

    print("🗑️ JARVIS: Clearing Word document...")
    try:
        word_app = win32com.client.GetActiveObject("Word.Application")
        word_app.Activate()
        word_app.ActiveDocument.Content.Delete()
        print("✅ JARVIS: Word document cleared.")
    except Exception as e:
        print(f"❌ Error: {e}")
        
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
            print(f"✅ JARVIS: Inserted text at paragraph {line_number}.")
        elif line_number == paragraphs.Count + 1:
            doc.Content.InsertAfter("\n" + text)
            print(f"✅ JARVIS: Appended text.")
    except Exception as e:
         print(f"❌ Error: {e}")

# -------- CURSOR MOVEMENTS & SPACING --------
def word_space():
    if focus_word(): pyautogui.press('space')

def word_new_line():
    if focus_word(): pyautogui.press('enter')

def word_new_paragraph():
    if focus_word():
        pyautogui.press('enter')
        pyautogui.press('enter')

def word_move_cursor(direction):
    if focus_word(): pyautogui.press(direction)

def word_insert_at_cursor(text):
    if focus_word():
        pyperclip.copy(text)
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'v')