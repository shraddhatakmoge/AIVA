import os
import re
import time
import json
import threading
import datetime
import winsound
from plyer import notification

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

REMINDERS_FILE = os.path.join(DATA_DIR, "aiva_reminders.json")

BEEP_FREQ = 1000
BEEP_DURATION = 600
POPUP_DURATION = 8
CHECK_INTERVAL = 5


def _beep():
    try:
        winsound.Beep(BEEP_FREQ, BEEP_DURATION)
        winsound.Beep(BEEP_FREQ + 200, BEEP_DURATION)
    except:
        pass


def _popup(label: str):
    try:
        notification.notify(
            title="Jarvis Reminder",
            message=label,
            app_name="Jarvis",
            timeout=POPUP_DURATION,
        )
    except:
        pass


def _load():
    if os.path.exists(REMINDERS_FILE):
        try:
            with open(REMINDERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []


def _save(reminders):
    with open(REMINDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(reminders, f, indent=2)


def _next_id(reminders):
    return max((r["id"] for r in reminders), default=0) + 1


def _parse_label(text: str) -> str:
    match = re.search(r"\bto\b\s+(.+)$", text, re.IGNORECASE)
    if match:
        return match.group(1).strip().capitalize()
    return text.strip().capitalize()


def _parse_countdown(text: str):
    match = re.search(r"in\s+(\d+)\s*(second|seconds|sec|minute|minutes|min|hour|hours|hr)", text, re.IGNORECASE)
    if match:
        amount = int(match.group(1))
        unit = match.group(2).lower()

        if "sec" in unit:
            delta = datetime.timedelta(seconds=amount)
        elif "min" in unit:
            delta = datetime.timedelta(minutes=amount)
        else:
            delta = datetime.timedelta(hours=amount)

        return datetime.datetime.now() + delta
    return None


def _parse_clock_time(text: str):
    match = re.search(r"at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", text, re.IGNORECASE)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0
        ampm = (match.group(3) or "").lower()

        if ampm == "pm" and hour != 12:
            hour += 12
        elif ampm == "am" and hour == 12:
            hour = 0

        now = datetime.datetime.now()
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        if target <= now:
            target += datetime.timedelta(days=1)

        return target
    return None


def _parse_repeat(text: str):
    t = text.lower()

    if re.search(r"every\s+day|everyday|daily", t):
        return 86400

    if re.search(r"every\s+hour", t):
        return 3600

    match = re.search(r"every\s+(\d+)\s*(minute|minutes|min|hour|hours|hr)", t)
    if match:
        amount = int(match.group(1))
        unit = match.group(2)
        return amount * 60 if "min" in unit else amount * 3600

    if "every" in t:
        return 86400

    return None


def _repeat_label(seconds: int) -> str:
    if seconds == 86400:
        return "every day"
    if seconds == 3600:
        return "every hour"
    return f"every {seconds // 60} minutes"


class ReminderEngine:
    def __init__(self):
        self.reminders = _load()
        self.lock = threading.Lock()
        self.running = False

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        while self.running:
            self._tick()
            time.sleep(CHECK_INTERVAL)

    def _tick(self):
        now = datetime.datetime.now()
        with self.lock:
            changed = False
            for r in self.reminders:
                if r.get("done"):
                    continue

                target = datetime.datetime.fromisoformat(r["trigger_time"])
                if now >= target:
                    label = r.get("label", "Reminder")
                    print(f"[REMINDER] {label}")

                    threading.Thread(target=_beep, daemon=True).start()
                    threading.Thread(target=_popup, args=(label,), daemon=True).start()

                    repeat = r.get("repeat_seconds")
                    if repeat:
                        r["trigger_time"] = (target + datetime.timedelta(seconds=repeat)).isoformat()
                    else:
                        r["done"] = True

                    changed = True

            if changed:
                _save(self.reminders)

    def parse_and_add(self, text: str):
        label = _parse_label(text)
        repeat = _parse_repeat(text)
        t = text.lower()

        if repeat and "at " in t:
            trigger = _parse_clock_time(text)
            if not trigger:
                trigger = datetime.datetime.now() + datetime.timedelta(seconds=repeat)

        elif "in " in t:
            trigger = _parse_countdown(text)
            if not trigger:
                return "Could not understand reminder time."

        elif "at " in t:
            trigger = _parse_clock_time(text)
            if not trigger:
                return "Could not understand reminder time."

        else:
            return "Say something like remind me in 10 minutes to drink water."

        with self.lock:
            reminder = {
                "id": _next_id(self.reminders),
                "label": label,
                "trigger_time": trigger.isoformat(),
                "repeat_seconds": repeat,
                "done": False,
                "created": datetime.datetime.now().isoformat(),
            }
            self.reminders.append(reminder)
            _save(self.reminders)

        t_str = trigger.strftime("%d %b %Y at %I:%M %p")

        if repeat:
            return f"Reminder set for {label}, {_repeat_label(repeat)}, starting {t_str}"
        return f"Reminder set for {label}, at {t_str}"

    def list_reminders(self):
        with self.lock:
            active = [r for r in self.reminders if not r.get("done")]

        if not active:
            return "No active reminders"

        lines = ["Active reminders:"]
        for r in active:
            t = datetime.datetime.fromisoformat(r["trigger_time"])
            rep = f" ({_repeat_label(r['repeat_seconds'])})" if r.get("repeat_seconds") else ""
            lines.append(f"{r['id']}. {r['label']} at {t.strftime('%I:%M %p')}{rep}")
        return "\n".join(lines)

    def delete_reminder(self, rid: int):
        with self.lock:
            for r in self.reminders:
                if r["id"] == rid and not r.get("done"):
                    r["done"] = True
                    _save(self.reminders)
                    return f"Reminder {rid} deleted"
        return f"Reminder {rid} not found"

    def clear_all(self):
        with self.lock:
            for r in self.reminders:
                r["done"] = True
            _save(self.reminders)
        return "All reminders cleared"


reminder_engine = ReminderEngine()


def handle_reminder_command(command: str):
    command = command.lower().strip()

    if any(x in command for x in ["remind me", "set reminder", "reminder", "every day", "every hour", "every "]):
        return reminder_engine.parse_and_add(command)

    if "list reminder" in command or "show reminder" in command or command == "reminders":
        return reminder_engine.list_reminders()

    match = re.search(r"(delete|remove)\s+reminder\s+(\d+)", command)
    if match:
        rid = int(match.group(2))
        return reminder_engine.delete_reminder(rid)

    if "clear reminders" in command or "delete all reminders" in command:
        return reminder_engine.clear_all()

    return None