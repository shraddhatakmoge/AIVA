import os
import time
import pyautogui
import pygetwindow as gw
import subprocess
import pyperclip

pyautogui.FAILSAFE = False


# -------- SPEAK --------
def speak(text):
    print("Assistant:", text)
    command = f"""
    Add-Type -AssemblyName System.Speech;
    $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer;
    $speak.Speak("{text}");
    """
    subprocess.run(["powershell", "-Command", command])


# -------- NOTEPAD --------
def open_notepad():
    speak("Opening Notepad")
    os.system("start notepad")
    time.sleep(2)


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
        speak("Writing")
        click_inside_notepad(win)
        pyautogui.write(text, interval=0.05)


# -------- NEW FILE --------
def new_file():
    win = focus_notepad()
    if win:
        speak("Opening new file")
        pyautogui.hotkey("ctrl", "n")


# -------- SAVE --------
def save_file(filename="notes.txt"):
    win = focus_notepad()
    if win:
        speak("Got it! Saving your file")
        pyautogui.hotkey("ctrl", "s")
        time.sleep(1)
        pyautogui.write(filename)
        pyautogui.press("enter")


# -------- CLEAR (FIXED) --------
def clear_notepad():
    win = focus_notepad()
    if win:
        speak("Clearing screen")

        click_inside_notepad(win)
        time.sleep(0.5)

        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.3)

        # force delete everything
        for _ in range(5):
            pyautogui.press("delete")


# -------- DELETE LINE --------
def delete_line():
    win = focus_notepad()
    if win:
        speak("Deleting last line")

        text = get_notepad_text(win)
        lines = text.split("\n")

        if lines:
            lines.pop()

        new_text = "\n".join(lines)

        pyperclip.copy(new_text)

        click_inside_notepad(win)
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.2)
        pyautogui.hotkey("ctrl", "v")


# -------- READ --------
def read_current_notepad():
    win = focus_notepad()
    if win:
        speak("Reading file")
        click_inside_notepad(win)

        pyautogui.hotkey("ctrl", "a")
        pyautogui.hotkey("ctrl", "c")

        text = pyperclip.paste()

        print("\n--- Notepad Content ---\n", text)

        for line in text.splitlines():
            if line.strip():
                speak(line)


# -------- REPLACE WORD (FIXED) --------
def replace_word(old, new):
    win = focus_notepad()
    if win:
        speak(f"Replacing {old} with {new}")
        click_inside_notepad(win)

        pyautogui.hotkey("ctrl", "a")
        pyautogui.hotkey("ctrl", "c")
        time.sleep(0.3)

        text = pyperclip.paste()
        text = text.replace(old, new)

        pyperclip.copy(text)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.hotkey("ctrl", "v")


# -------- CLEAR WORD --------
def clear_word(word):
    win = focus_notepad()
    if win:
        speak(f"Removing {word}")

        text = get_notepad_text(win)
        text = text.replace(word, "")

        pyperclip.copy(text)

        click_inside_notepad(win)
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.2)
        pyautogui.hotkey("ctrl", "v")


# -------- UNDO --------
def undo_action():
    win = focus_notepad()
    if win:
        speak("Undoing last action")
        click_inside_notepad(win)
        pyautogui.hotkey("ctrl", "z")


# -------- REDO --------
def redo_action():
    win = focus_notepad()
    if win:
        speak("Redoing last action")
        click_inside_notepad(win)
        pyautogui.hotkey("ctrl", "y")


# -------- DELETE WORD FROM LINE --------
def delete_word_in_line(word, line_number):
    win = focus_notepad()
    if win:
        speak(f"Removing {word} from line {line_number}")

        text = get_notepad_text(win)
        lines = text.split("\n")

        if 0 < line_number <= len(lines):
            words = lines[line_number - 1].split()

            # remove only exact match
            words = [w for w in words if w.lower() != word.lower()]

            # rebuild line
            lines[line_number - 1] = " ".join(words)

        else:
            speak("Invalid line number")
            return

        new_text = "\n".join(lines)

        pyperclip.copy(new_text)

        click_inside_notepad(win)
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.2)
        pyautogui.hotkey("ctrl", "v")


# -------- COPY ----------
def get_notepad_text(win):
    click_inside_notepad(win)
    time.sleep(0.5)

    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.2)

    pyautogui.hotkey("ctrl", "c")
    time.sleep(0.5)

    return pyperclip.paste()


# -------- CURSOR MOVE --------
def move_cursor(direction):
    win = focus_notepad()
    if win:
        speak(f"Moving {direction}")

        try:
            if win.isMinimized:
                win.restore()
            win.activate()
            time.sleep(0.5)
        except:
            pass

        # force focus inside notepad
        click_inside_notepad(win)
        time.sleep(0.3)

        if direction == "up":
            pyautogui.press("up")
        elif direction == "down":
            pyautogui.press("down")
        elif direction == "left":
            pyautogui.press("left")
        elif direction == "right":
            pyautogui.press("right")


# -------- NEW LINE --------
def new_line():
    speak("Going to new line")
    write_text("\n")


def new_paragraph():
    speak("Going to new paragraph")
    write_text("\n\n")


# -------- READ FILE --------
def read_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()

        print("\n--- File Content ---\n")
        print(content)

        speak("Reading file")
        for line in content.splitlines():
            speak(line)

    except:
        speak("File not found")


# ----------- NLP -----------
def process_command(cmd):
    cmd = cmd.lower()

    # -------- WRITE --------
    if "write" in cmd or "type" in cmd:
        text = cmd

        remove_words = [
            "please",
            "can you",
            "could you",
            "write",
            "type",
            "in notepad",
            "on notepad",
        ]

        for word in remove_words:
            text = text.replace(word, "")

        text = text.strip()

        if text:
            speak("Writing that for you")
            write_text(text)
        else:
            speak("What should I write?")

    # -------- OPEN NOTEPAD --------
    elif "notepad" in cmd:
        open_notepad()

    # -------- SAVE --------
    elif "save" in cmd:
        filename = "notes.txt"
        for word in cmd.split():
            if ".txt" in word:
                filename = word
        save_file(filename)

    # -------- CLEAR --------
    elif "clear" in cmd:
        clear_notepad()

    # -------- DELETE WORD FROM LINE --------
    elif "delete word" in cmd and "line" in cmd:
        try:
            words = cmd.split()

            word = words[words.index("word") + 1]
            line_number = int(words[words.index("line") + 1])

            delete_word_in_line(word, line_number)

        except:
            speak("Please say like delete word hello from line 2")

    # -------- DELETE LINE --------
    elif "delete" in cmd and "line" in cmd:
        delete_line()

    # -------- REPLACE --------
    elif "replace" in cmd and "with" in cmd:
        parts = cmd.split("replace")[-1].split("with")
        if len(parts) == 2:
            replace_word(parts[0].strip(), parts[1].strip())
        else:
            speak("Say replace X with Y")

    # -------- NEW LINE --------
    elif "new line" in cmd:
        new_line()

    elif "paragraph" in cmd:
        new_paragraph()

    # ------- NEW FILE -------
    elif "new file" in cmd:
        new_file()

    # -------- READ --------
    elif "read" in cmd:
        read_current_notepad()

    # -------- GREETING --------
    elif cmd in ["hi", "hello", "hey"]:
        speak("Hello! How can I help you?")

    # -------- UNDO --------
    elif "undo" in cmd:
        undo_action()

    # -------- CURSOR MOVE -------
    elif "move up" in cmd:
        move_cursor("up")

    elif "move down" in cmd:
        move_cursor("down")

    elif "move left" in cmd:
        move_cursor("left")

    elif "move right" in cmd:
        move_cursor("right")

    # -------- REDO --------
    elif "redo" in cmd:
        redo_action()

    # -------- DELETE WORD FROM LINE --------
    elif "delete word" in cmd and "line" in cmd:
        try:
            words = cmd.split()

            word = words[words.index("word") + 1]
            line_number = int(words[words.index("line") + 1])

            delete_word_in_line(word, line_number)

        except:
            speak("Please say like delete word hello from line 2")

    else:
        speak("Sorry, I didn’t understand that")


# -------- MAIN --------
if __name__ == "__main__":
    speak("Assistant started")

    while True:
        cmd = input("You: ").strip()

        if cmd.lower() == "exit":
            speak("Goodbye")
            break

        process_command(cmd)
