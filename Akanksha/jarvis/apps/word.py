import os
import time
import pyautogui
import pygetwindow as gw
from common import open_app_by_name, close_app
import win32com.client




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
    if focus_word():
        # Word's native shortcut for styles is Ctrl + Alt + (1, 2, or 3)
        if 1 <= level <= 3:
            pyautogui.hotkey('ctrl', 'alt', str(level))
            print(f"✅ Applied Heading {level}")
    else:
        print("❌ Word is not open!")
        
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