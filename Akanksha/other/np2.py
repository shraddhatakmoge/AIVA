import os
import time
import pyautogui
import pygetwindow as gw


# -------- GET NOTEPAD --------
def get_notepad():
    windows = gw.getWindowsWithTitle("Notepad")

    if not windows:
        os.system("start notepad")
        time.sleep(1.5)
        windows = gw.getWindowsWithTitle("Notepad")

    return windows[0] if windows else None


# -------- FOCUS + CLICK --------
def focus_notepad():
    win = get_notepad()

    if not win:
        print("Notepad not found")
        return None

    try:
        if win.isMinimized:
            win.restore()
        win.activate()
        time.sleep(0.5)
    except:
        pass

    # click inside
    x = win.left + win.width // 2
    y = win.top + win.height // 2
    pyautogui.click(x, y)
    time.sleep(0.2)

    return win


# -------- OPEN + TYPE --------
def open_and_write(text):
    os.system("start notepad")
    time.sleep(1.5)

    focus_notepad()
    pyautogui.write(text, interval=0.05)


# -------- TYPE --------
def write_text(text):
    focus_notepad()
    pyautogui.write(text, interval=0.05)


# -------- NEW LINE --------
def new_line():
    focus_notepad()
    pyautogui.press("enter")


# -------- DELETE CURRENT LINE --------
def delete_line():
    focus_notepad()

    # go to start
    pyautogui.press("home")
    time.sleep(0.1)

    # select line
    pyautogui.keyDown("shift")
    pyautogui.press("end")
    pyautogui.keyUp("shift")

    # delete
    pyautogui.press("delete")


# -------- MOVE CURSOR --------
def move_cursor(direction):
    focus_notepad()

    if direction == "up":
        pyautogui.press("up")
    elif direction == "down":
        pyautogui.press("down")
    elif direction == "left":
        pyautogui.press("left")
    elif direction == "right":
        pyautogui.press("right")


# -------- SAVE FILE --------
def save_file(filename="notes.txt"):
    focus_notepad()

    pyautogui.hotkey("ctrl", "s")
    time.sleep(1)

    pyautogui.write(filename)
    pyautogui.press("enter")


# -------- COMMAND SYSTEM --------
def process_command(cmd):
    cmd = cmd.lower()

    if "open notepad and type" in cmd:
        text = cmd.replace("open notepad and type", "").strip()
        open_and_write(text)

    elif cmd.startswith("type"):
        text = cmd.replace("type", "").strip()
        write_text(text)

    elif "new line" in cmd:
        new_line()

    elif "delete line" in cmd:
        delete_line()

    elif "move up" in cmd:
        move_cursor("up")

    elif "move down" in cmd:
        move_cursor("down")

    elif "move left" in cmd:
        move_cursor("left")

    elif "move right" in cmd:
        move_cursor("right")

    elif "save file" in cmd:
        parts = cmd.split()
        filename = parts[-1] if ".txt" in parts[-1] else "notes.txt"
        save_file(filename)

    else:
        print("Command not recognized")


# -------- MAIN --------
while True:
    cmd = input("You: ")

    if cmd == "exit":
        break

    process_command(cmd)