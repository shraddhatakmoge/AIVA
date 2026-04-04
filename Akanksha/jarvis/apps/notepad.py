import os
import time
import pyautogui
import pygetwindow as gw
import subprocess
import pyperclip
import pyttsx3
from common import open_system_app, close_app

engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()
    
    
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.1




# -------- OPEN --------
def open_notepad():
    
    os.system("start notepad")
    time.sleep(2)

# ---------- CLOSE ---------
def close_notepad():
    print("❌ Closing Notepad...")
    close_app("notepad")

# -------- FOCUS --------
def focus_notepad():
    windows = gw.getWindowsWithTitle("Notepad")

    for win in windows:
        try:
            if win.isMinimized:
                win.restore()
            win.activate()
            time.sleep(0.5)
            return win
        except:
            continue

    open_notepad()
    windows = gw.getWindowsWithTitle("Notepad")
    return windows[0] if windows else None


def click_inside_notepad(win):
    if win:
        x = win.left + win.width // 2
        y = win.top + win.height // 2
        pyautogui.click(x, y)
        time.sleep(0.3)


# -------- WRITE --------
def write_text(text):
    win = focus_notepad() # Get the window object
    if win:
        # Click the middle of the Notepad window to set the cursor
        x = win.left + win.width // 2
        y = win.top + win.height // 2
        pyautogui.click(x, y)
        time.sleep(0.2)
        
        # Now type
        pyautogui.write(text, interval=0.01)
        print(f"✅ Typed: {text}")

# ------ NEW FILe ------
def new_file():
    win = focus_notepad()
    if win:
        pyautogui.hotkey("ctrl", "n")
        
# -------- SAVE --------
def save_file(filename="notes.txt"):
    global current_file

    win = focus_notepad()
    if win:
        pyautogui.hotkey("ctrl", "s")
        time.sleep(1)

        pyautogui.hotkey("ctrl", "a")
        pyautogui.write(filename)
        pyautogui.press("enter")

        # ✅ FIXED PATH
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        current_file = os.path.join(desktop, filename)

        print("Saved at:", current_file)

# ------ READ ------
def read_notepad():
    win = focus_notepad()
    if win:
        click_inside_notepad(win)
        time.sleep(0.5)

        # ✅ CLEAR CLIPBOARD FIRST
        pyperclip.copy("")
        time.sleep(0.2)

        # Copy from Notepad
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.3)
        pyautogui.hotkey("ctrl", "c")
        time.sleep(0.5)

        text = pyperclip.paste()

        # ✅ REMOVE ALL WHITESPACE
        visible_text = "".join(text.split())

        if visible_text == "":
            print("There is no text")
            speak("There is no text")
            return

        print("\n--- Notepad Content ---\n")
        print(text)

        # 🔊 Speak content
        for line in text.splitlines():
            if line.strip():
                speak(line)
            
# -------- REPLACE WORD --------
def replace_word(old, new):
    win = focus_notepad()
    if win:
        speak(f"Replacing {old} with {new}")
        click_inside_notepad(win)
        time.sleep(0.5)

        # Clear clipboard first (important)
        pyperclip.copy("")
        time.sleep(0.2)

        # Copy full text
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.3)
        pyautogui.hotkey("ctrl", "c")
        time.sleep(0.5)

        text = pyperclip.paste()

        if not text.strip():
            print("❌ There is no text")
            speak("There is no text")
            return

        # Replace text natively in Python
        new_text = text.replace(old, new)

        # Copy new text to clipboard
        pyperclip.copy(new_text)
        time.sleep(0.2)

        # Paste back into Notepad
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.3)
        pyautogui.hotkey("ctrl", "v")

        print(f"✅ Replaced '{old}' with '{new}'")
                
# -------- DELETE WORD (PRESERVES NEWLINES) ------
def delete_word(word):
    win = focus_notepad()
    if win:
        click_inside_notepad(win)
        time.sleep(0.5)

        # Clear clipboard (important)
        pyperclip.copy("")
        time.sleep(0.2)

        # Copy all text
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.3)
        pyautogui.hotkey("ctrl", "c")
        time.sleep(0.5)

        text = pyperclip.paste()

        if not text.strip():
            print("There is no text")
            speak("There is no text")
            return

        # 🔥 THE FIX: Process the document line-by-line to protect your paragraphs
        lines = text.split('\n')
        new_lines = []
        
        for line in lines:
            # Split only the words on this specific line
            words = line.split() 
            # Filter out the target word
            words = [w for w in words if w.lower() != word.lower()]
            # Rejoin the line
            new_lines.append(" ".join(words))

        # Glue the document back together using newlines (\n) instead of spaces
        new_text = "\n".join(new_lines)

        # Put updated text back
        pyperclip.copy(new_text)
        time.sleep(0.2)

        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.3)
        pyautogui.hotkey("ctrl", "v")
        
        # 🔥 THE FIX (Part 2): Move cursor to the bottom so the screen doesn't jump to the top
        time.sleep(0.2)
        pyautogui.hotkey("ctrl", "end")

        print(f"✅ Deleted word '{word}'")

# --------- NEW LINE --------
def new_line():
    win = focus_notepad()
    if win:
        click_inside_notepad(win)
        pyautogui.press("enter")
        print("New line added")

# --------- INSERT TEXT AT CURSOR -----
def insert_at_cursor(text):
    win = focus_notepad()
    if not win:
        print("❌ Could not find or open Notepad.")
        return

    # ⚠️ CRITICAL: Do NOT call click_inside_notepad() here!
    # Clicking will move the user's cursor to the middle of the screen.
    # focus_notepad() already brought the window to the front.
    time.sleep(0.2) # Just a tiny pause to let Windows focus settle

    # Use clipboard pasting instead of pyautogui.write(). 
    # It is instant and avoids typos if the computer lags.
    pyperclip.copy(text)
    time.sleep(0.1)
    
    pyautogui.hotkey("ctrl", "v")

    print(f"✅ Inserted '{text}' at the current cursor position")
        
# --------- INSERT TEXT AT LINE -----
def insert_text_at_line(text_to_insert, line_number):
    win = focus_notepad()
    if not win:
        print("❌ Could not find or open Notepad.")
        return

    click_inside_notepad(win)
    time.sleep(0.2)

    # 1. Clear clipboard with a marker
    pyperclip.copy("EMPTY_MARKER")
    time.sleep(0.1)

    # 2. Select All and Copy
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.2)
    pyautogui.hotkey("ctrl", "c")
    time.sleep(0.4)

    text = pyperclip.paste()

    # Edge Case: If Notepad is completely empty!
    if text == "EMPTY_MARKER" or not text.strip():
        if line_number == 1:
            pyperclip.copy(text_to_insert)
            pyautogui.hotkey("ctrl", "v")
            print(f"✅ Inserted '{text_to_insert}' at line 1 (Blank file)")
            return
        else:
            print("⚠️ Notepad is empty! Cannot insert at that line yet.")
            return

    # Safety: Don't paste Python code
    if "def " in text and "import " in text:
        print("⚠️ Warning: Grabbed script code instead of Notepad text. Aborting.")
        return

    # 3. Process the text in Python
    # Remove hidden carriage returns (\r) that Windows adds, then split by newline
    lines = text.replace('\r', '').split("\n")

    # Check if the line exists
    if 0 < line_number <= len(lines):
        
        target_line = lines[line_number - 1]
        
        # If the line already has words, add a space before inserting
        if target_line.strip() == "":
            lines[line_number - 1] = text_to_insert
        else:
            lines[line_number - 1] = target_line + " " + text_to_insert

        new_text = "\n".join(lines)

        # 4. Paste back
        pyperclip.copy(new_text)
        time.sleep(0.2)
        
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.2)
        
        # Move cursor to end so the screen doesn't jump
        pyautogui.hotkey("ctrl", "end")
        
        print(f"✅ Inserted '{text_to_insert}' at line {line_number}")
        
    # Bonus Feature: If they ask for Line 5, but there are only 4 lines, append it!
    elif line_number == len(lines) + 1:
        lines.append(text_to_insert)
        new_text = "\n".join(lines)
        pyperclip.copy(new_text)
        time.sleep(0.2)
        pyautogui.hotkey("ctrl", "v")
        pyautogui.hotkey("ctrl", "end")
        print(f"✅ Appended '{text_to_insert}' to new line {line_number}")
        
    else:
        print(f"❌ Invalid line. Document only has {len(lines)} lines.")
   
# ------ CURSOR MOVE -----
def move_cursor(direction):
    win = focus_notepad()
    if win:
        # ❌ REMOVE click_inside_notepad(win)
        time.sleep(0.2)

        pyautogui.press(direction)

        print(f"Moved cursor {direction}")
             
# ------- NEW PARAGRAPH ----------
def new_paragraph():
    win = focus_notepad()
    if win:
        click_inside_notepad(win)
        pyautogui.press("enter")
        pyautogui.press("enter")
        print("New paragraph added")

# ----- DELETE WORD FROM LINE -----

def delete_word_from_line(word, line_number):
    win = focus_notepad()
    if not win:
        print("❌ Could not find or open Notepad.")
        return

    # Click to ensure focus
    click_inside_notepad(win)
    time.sleep(0.2)

    # 1. Clear clipboard with a marker
    pyperclip.copy("EMPTY_MARKER")
    time.sleep(0.1)

    # 2. Select All and Copy to Python
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.2)
    pyautogui.hotkey("ctrl", "c")
    time.sleep(0.4)

    text = pyperclip.paste()

    # Safety checks
    if text == "EMPTY_MARKER" or not text.strip():
        print("⚠️ Notepad is empty or copy failed.")
        return
    if "def " in text and "import " in text:
        print("⚠️ Warning: Grabbed script code instead of Notepad text. Aborting.")
        return

    # 3. Process the exact line in Python Memory
    lines = text.split("\n")
    
    # Check if the line number actually exists in the file
    if 0 < line_number <= len(lines):
        
        # Grab the target line (Python lists start at 0, so line 1 is index 0)
        target_line = lines[line_number - 1]
        
        # Split line into words and remove the target word
        words = target_line.split()
        new_words = [w for w in words if w.lower() != word.lower()]
        
        # Put the line back together
        lines[line_number - 1] = " ".join(new_words)
        
        # Put the whole document back together
        new_text = "\n".join(lines)
        
        # 4. Copy and Paste back into Notepad
        pyperclip.copy(new_text)
        time.sleep(0.2)
        
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.2)
        
        # Move cursor to the end so it doesn't jump to the top
        pyautogui.hotkey("ctrl", "end")
        
        print(f"✅ Removed '{word}' from line {line_number}")
    else:
        print(f"❌ Invalid line. The document only has {len(lines)} lines.")
    
# --------- UNDO (STABILIZED) --------
def undo_action():
    win = focus_notepad()
    if win:
        click_inside_notepad(win)
        time.sleep(0.2) # ⏳ Wait to guarantee Notepad has focus

        # The interval=0.1 forces Python to hold Ctrl, hold Z, release Z, release Ctrl.
        pyautogui.hotkey("ctrl", "z", interval=0.1)
        print("✅ Undo executed")

# ------ REDO (STABILIZED) -----------
def redo_action():
    win = focus_notepad()
    if win:
        click_inside_notepad(win)
        time.sleep(0.2)

        # In Windows 11, Redo is standard as Ctrl+Y 
        pyautogui.hotkey("ctrl", "y", interval=0.1)
        print("✅ Redo executed")
                   
# -------- CLEAR --------
def clear_notepad():
    win = focus_notepad()
    if win:
        click_inside_notepad(win)
        time.sleep(0.2) # Add a small delay to ensure focus
        
        # Select all text
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.2) # Wait for selection
        
        # Press backspace (often more reliable than delete in Notepad)
        pyautogui.press("backspace") 
        print("✅ Notepad cleared")


# -------- DELETE LINE --------
def delete_line():
    win = focus_notepad()
    if win:
        pyautogui.hotkey("ctrl", "a")
        pyautogui.press("delete")
        
# ----- PRESS SPACE -----
def press_space():
    win = focus_notepad()
    if not win:
        print("❌ Could not find or open Notepad.")
        return

    # Just a tiny pause to let Windows focus settle, no clicking!
    time.sleep(0.2) 
    
    pyautogui.press("space")
    print("✅ Pressed Space")


# -------- MAIN COMMAND HANDLER --------
def process_notepad_command(cmd):
    cmd = cmd.lower()

    if "open notepad" in cmd:
        open_notepad()

    elif cmd.startswith("write "):
        text = cmd.replace("write", "", 1).strip()
        write_text(text)

    elif "save" in cmd:
        words = cmd.split()

        filename = None
        for word in words:
            if ".txt" in word:
                filename = word
                break

        if filename:
            save_file(filename)
        else:
            print("❌ Please say: save filename.txt")

    elif "insert" in cmd and "line" in cmd:
        try:
            parts = cmd.split("insert")[-1].split("at line")
            text_to_insert = parts[0].strip()
            line_number = int(parts[1].strip())

            insert_text_at_line(text_to_insert, line_number)
        except:
            print("❌ Say: insert hello at line 2")
        
        # ✅ FIRST: specific line delete
    elif "delete word" in cmd and "line" in cmd:
        try:
            words = cmd.split()

            word = words[words.index("word") + 1]
            line_number = int(words[words.index("line") + 1])

            delete_word_from_line(word, line_number)

        except:
            print("❌ Say: delete word hello from line 2")


        # ✅ THEN: general delete
    elif "delete word" in cmd:
        try:
            word = cmd.split("delete word")[-1].strip()
            delete_word(word)
        except:
            print("❌ Say: delete word hello")
       
    elif cmd.startswith("insert "):
        text = cmd.replace("insert", "", 1).strip()
        insert_at_cursor(text)
    
    elif cmd == "move left":
        move_cursor("left")

    elif cmd == "move right":
        move_cursor("right")

    elif cmd == "move up":
        move_cursor("up")

    elif cmd == "move down":
        move_cursor("down")
     
    elif "new file" in cmd:
        new_file()
        
    elif "read" in cmd:
        read_notepad()

    elif "clear" in cmd:
        clear_notepad()

    elif "new paragraph" in cmd:
        new_paragraph()

    elif "new line" in cmd:
        new_line()
        
    elif "replace" in cmd and "with" in cmd:
        try:
            parts = cmd.split("replace")[-1].split("with")
            old = parts[0].strip()
            new = parts[1].strip()

            replace_word(old, new)
        except:
            print("❌ Say: replace oldword with newword")
            
    elif "undo" in cmd:
        undo_action()

    elif "redo" in cmd:
        redo_action()
        
    elif "delete line" in cmd:
        delete_line()

    else:
        return False

    return True 