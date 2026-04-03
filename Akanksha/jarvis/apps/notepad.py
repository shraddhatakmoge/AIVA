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
    win = focus_notepad()
    if win:
        click_inside_notepad(win)
        pyautogui.write(text, interval=0.05)

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
            print("There is no text")
            speak("There is no text")
            return

        # Replace text
        new_text = text.replace(old, new)

        # Copy new text
        pyperclip.copy(new_text)
        time.sleep(0.2)

        # Paste back
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.3)
        pyautogui.hotkey("ctrl", "v")

        print(f"Replaced '{old}' with '{new}'")
                
# -------- DELETE WORD ------
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

        # Remove only exact word
        words = text.split()
        words = [w for w in words if w.lower() != word.lower()]
        new_text = " ".join(words)

        # Put updated text back
        pyperclip.copy(new_text)
        time.sleep(0.2)

        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.3)
        pyautogui.hotkey("ctrl", "v")

        print(f"Deleted word '{word}'")

# --------- NEW LINE --------
def new_line():
    win = focus_notepad()
    if win:
        click_inside_notepad(win)
        pyautogui.press("enter")
        print("New line added")

# --------- INSERT AT CURSOR -----
def insert_at_cursor(text):
    win = focus_notepad()
    if win:
        # ❌ DO NOT click (it changes cursor position)
        win.activate()
        time.sleep(0.2)

        pyautogui.write(text, interval=0.05)

        print(f"Inserted '{text}' at cursor")
        
# --------- INSERT TEXT AT LINE -----
def insert_text_at_line(text_to_insert, line_number):
    win = focus_notepad()
    if win:
        click_inside_notepad(win)
        time.sleep(0.5)

        # Clear clipboard
        pyperclip.copy("")
        time.sleep(0.2)

        # Copy full text
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.3)
        pyautogui.hotkey("ctrl", "c")
        time.sleep(0.5)

        text = pyperclip.paste()

        lines = text.split("\n")

        if line_number <= len(lines):
            lines[line_number - 1] += " " + text_to_insert
        else:
            print("❌ Invalid line number")
            return

        new_text = "\n".join(lines)

        # Paste updated text
        pyperclip.copy(new_text)
        time.sleep(0.2)

        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.3)
        pyautogui.hotkey("ctrl", "v")

        print(f"Inserted text at line {line_number}")
   
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
        
# -------- DELETE WORD FROM LINE ----
def delete_word_from_line(word, line_number):
    win = focus_notepad()
    if win:
        click_inside_notepad(win)
        time.sleep(0.5)

        # Clear clipboard
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

        lines = text.split("\n")

        # Check valid line
        if 0 < line_number <= len(lines):
            words = lines[line_number - 1].split()

            # remove only matching word
            words = [w for w in words if w.lower() != word.lower()]

            lines[line_number - 1] = " ".join(words)
        else:
            print("❌ Invalid line number")
            return

        new_text = "\n".join(lines)

        # Paste updated text
        pyperclip.copy(new_text)
        time.sleep(0.2)

        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.3)
        pyautogui.hotkey("ctrl", "v")

        print(f"Deleted '{word}' from line {line_number}")
                 
# --------- UNDO --------
def undo_action():
    win = focus_notepad()
    if win:
        click_inside_notepad(win)
        pyautogui.hotkey("ctrl", "z")
        print("Undo done")

# ------ REDO -----------
def redo_action():
    win = focus_notepad()
    if win:
        click_inside_notepad(win)
        pyautogui.hotkey("ctrl", "y")
        print("Redo done")
                   
# -------- CLEAR --------
def clear_notepad():
    win = focus_notepad()
    if win:
        click_inside_notepad(win)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.press("delete")


# -------- DELETE LINE --------
def delete_line():
    win = focus_notepad()
    if win:
        pyautogui.hotkey("ctrl", "a")
        pyautogui.press("delete")


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