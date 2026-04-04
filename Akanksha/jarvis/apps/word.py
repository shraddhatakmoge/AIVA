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
    pyautogui.press('f12')  # F12 instantly opens the "Save As" dialog in Word
    time.sleep(1.5)
    
    if folder_path:
        # Combine the folder path and filename (e.g., C:\Users\Name\Desktop\MyDoc.docx)
        full_path = os.path.join(folder_path, filename)
        pyautogui.write(full_path)
    else:
        pyautogui.write(filename)
        
    time.sleep(0.5)
    pyautogui.press('enter')
    print(f"✅ Document saved as: {filename}")

# -------- 7. TEXT STYLING --------
def apply_style(style_type):
    if style_type == "bold":
        pyautogui.hotkey('ctrl', 'b')
    elif style_type == "italic":
        pyautogui.hotkey('ctrl', 'i')
    elif style_type == "underline":
        pyautogui.hotkey('ctrl', 'u')
    print(f"✅ Applied style: {style_type}")

# -------- 8. ALIGNMENT --------
def set_alignment(align):
    if align == "left":
        pyautogui.hotkey('ctrl', 'l')
    elif align == "center":
        pyautogui.hotkey('ctrl', 'e')
    elif align == "right":
        pyautogui.hotkey('ctrl', 'r')
    elif align == "justify":
        pyautogui.hotkey('ctrl', 'j')
    print(f"✅ Text aligned: {align}")

# -------- 9. HEADINGS --------
def apply_heading(level):
    # Word's native shortcut for styles is Ctrl + Alt + (1, 2, or 3)
    if 1 <= level <= 3:
        pyautogui.hotkey('ctrl', 'alt', str(level))
        print(f"✅ Applied Heading {level}")