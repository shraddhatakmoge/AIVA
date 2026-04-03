import os
import re
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HISTORY_FILE = os.path.join(BASE_DIR, "command_history.log")

MAX_CACHE = 1000
command_cache = []
pending_delete = False


NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "twenty": 20,
}


def load_history():
    global command_cache
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            command_cache = [line.strip() for line in f.readlines()]
    else:
        command_cache = []


def log_command(command: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"{timestamp} | {command}"

    command_cache.append(entry)

    if len(command_cache) > MAX_CACHE:
        command_cache.pop(0)

    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(entry + "\n")


def get_last_commands(count=10):
    return command_cache[-count:]


def extract_history_count(command: str):
    number_match = re.search(r'(\d+)', command)
    if number_match:
        return int(number_match.group(1))

    for word, value in NUMBER_WORDS.items():
        if re.search(rf'\b{word}\b', command):
            return value

    return 10


def handle_history_command(command: str):
    command = command.lower()

    if "history" not in command and "command" not in command:
        return None

    full_keywords = [
        "all history",
        "total history",
        "complete history",
        "entire history",
        "all commands",
        "full history"
    ]

    if any(word in command for word in full_keywords):
        history = command_cache
        if not history:
            return "No command history available"
        return "Complete command history:\n" + "\n".join(history)

    count = extract_history_count(command)
    history = get_last_commands(count)

    if not history:
        return "No command history available"

    # Short spoken-friendly version for small requests
    if count <= 5:
        spoken_lines = []
        for i, item in enumerate(history, 1):
            try:
                spoken_lines.append(f"{i}. {item.split('|', 1)[1].strip()}")
            except:
                spoken_lines.append(f"{i}. {item}")
        return f"Last {len(history)} commands:\n" + "\n".join(spoken_lines)

    return f"Last {len(history)} commands:\n" + "\n".join(history)


def delete_history():
    global command_cache
    command_cache = []

    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            f.write("")

    return "Command history deleted successfully"

def handle_delete_history(command: str):
    global pending_delete
    command = command.lower().strip()

    if "delete" in command and "history" in command:
        pending_delete = True
        return "Are you sure you want to delete all command history? Say yes or no."

    if "clear" in command and "history" in command:
        pending_delete = True
        return "Are you sure you want to delete all command history? Say yes or no."

    if pending_delete:
        yes_words = [
            "yes", "yeah", "yup", "confirm", "do it",
            "delete it", "yes delete", "yes delete the history"
        ]

        no_words = [
            "no", "nope", "cancel", "don't", "do not", "stop"
        ]

        cleaned = command.lower().strip()

        if any(word in cleaned for word in yes_words):
            pending_delete = False
            return delete_history()

        if any(word in cleaned for word in no_words):
            pending_delete = False
            return "History deletion cancelled"

    return None


def is_waiting_for_history_confirmation():
    return pending_delete