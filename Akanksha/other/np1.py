import os
import time
import shutil

FILE_NAME = "notes.txt"
BACKUP_FILE = "backup.txt"

current_line = 0
current_col = 0


# -------- FILE SAFETY --------
def backup():
    if os.path.exists(FILE_NAME):
        shutil.copy(FILE_NAME, BACKUP_FILE)


def undo():
    if os.path.exists(BACKUP_FILE):
        shutil.copy(BACKUP_FILE, FILE_NAME)
        print("Undo done")


# -------- FILE HANDLING --------
def get_lines():
    if not os.path.exists(FILE_NAME):
        open(FILE_NAME, "w").close()

    with open(FILE_NAME, "r") as f:
        return f.readlines()


def save_lines(lines):
    with open(FILE_NAME, "w") as f:
        f.writelines(lines)


# -------- OPEN --------
def open_notepad():
    os.system(f"start notepad {FILE_NAME}")
    time.sleep(1)


# -------- WRITE --------
def write_text(text):
    global current_line
    backup()

    lines = get_lines()

    while len(lines) <= current_line:
        lines.append("\n")

    lines[current_line] = lines[current_line].strip() + " " + text + "\n"

    save_lines(lines)
    open_notepad()


# -------- INSERT --------
def insert_line(n, text):
    backup()
    lines = get_lines()
    lines.insert(n - 1, text + "\n")
    save_lines(lines)
    open_notepad()


# -------- REPLACE LINE --------
def replace_line(n, text):
    backup()
    lines = get_lines()

    if 0 < n <= len(lines):
        lines[n - 1] = text + "\n"

    save_lines(lines)
    open_notepad()


# -------- DELETE LINE --------
def delete_line(n=None):
    global current_line
    backup()

    lines = get_lines()
    index = current_line if n is None else n - 1

    if 0 <= index < len(lines):
        lines.pop(index)

    save_lines(lines)
    current_line = max(0, index - 1)
    open_notepad()


# -------- WORD OPERATIONS --------
def replace_word(old, new):
    backup()
    text = "".join(get_lines()).replace(old, new)

    with open(FILE_NAME, "w") as f:
        f.write(text)

    open_notepad()


def delete_word(word):
    replace_word(word, "")


# -------- CURSOR SYSTEM --------
def go_to_line(n):
    global current_line
    current_line = max(0, n - 1)
    print(f"Cursor at line {n}")


def move_cursor(direction):
    global current_line, current_col

    if direction == "up":
        current_line = max(0, current_line - 1)

    elif direction == "down":
        current_line += 1

    elif direction == "left":
        current_col = max(0, current_col - 1)

    elif direction == "right":
        current_col += 1

    print(f"Cursor → line {current_line + 1}, col {current_col}")


def show_cursor():
    print(f"Current position → line {current_line + 1}, col {current_col}")


# -------- SELECTION --------
def highlight_line(n):
    lines = get_lines()

    print("\n--- HIGHLIGHT ---\n")
    for i, line in enumerate(lines, 1):
        if i == n:
            print(">>", line.strip())
        else:
            print("  ", line.strip())


def highlight_range(start, end):
    lines = get_lines()

    print("\n--- SELECTED RANGE ---\n")
    for i, line in enumerate(lines, 1):
        if start <= i <= end:
            print(">>", line.strip())
        else:
            print("  ", line.strip())


# -------- NEW LINE --------
def new_line():
    global current_line
    current_line += 1


def new_paragraph():
    global current_line
    current_line += 2


# -------- CLEAR --------
def clear_file():
    backup()
    open(FILE_NAME, "w").close()
    open_notepad()


# -------- MAIN --------
while True:
    cmd = input("You: ").lower()

    if cmd == "exit":
        break

    elif "open notepad" in cmd:
        open_notepad()

    elif "write" in cmd:
        text = cmd.replace("write", "").strip()
        write_text(text)

    elif "insert line" in cmd:
        parts = cmd.split()
        n = int(parts[2])
        text = " ".join(parts[3:])
        insert_line(n, text)

    elif "replace line" in cmd:
        parts = cmd.split()
        n = int(parts[2])
        text = " ".join(parts[3:])
        replace_line(n, text)

    elif "delete line" in cmd:
        try:
            n = int(cmd.split()[-1])
            delete_line(n)
        except:
            delete_line()

    elif "replace" in cmd and "with" in cmd:
        parts = cmd.split("replace")[-1].split("with")
        replace_word(parts[0].strip(), parts[1].strip())

    elif "delete word" in cmd:
        word = cmd.split()[-1]
        delete_word(word)

    elif "highlight line" in cmd:
        n = int(cmd.split()[-1])
        highlight_line(n)

    elif "highlight from" in cmd:
        parts = cmd.split()
        start = int(parts[2])
        end = int(parts[-1])
        highlight_range(start, end)

    elif "go to line" in cmd:
        n = int(cmd.split()[-1])
        go_to_line(n)

    elif "move up" in cmd:
        move_cursor("up")

    elif "move down" in cmd:
        move_cursor("down")

    elif "move left" in cmd:
        move_cursor("left")

    elif "move right" in cmd:
        move_cursor("right")

    elif "where am i" in cmd:
        show_cursor()

    elif "new line" in cmd:
        new_line()

    elif "new paragraph" in cmd:
        new_paragraph()

    elif "clear" in cmd:
        clear_file()

    elif "undo" in cmd:
        undo()

    else:
        print("Command not recognized")