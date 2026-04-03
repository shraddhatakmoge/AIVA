import threading
import time
import re
import tkinter as tk
import pygame
import os
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RINGTONE_PATH = os.path.join(BASE_DIR, "assets", "sounds", "alarm.mp3")

pygame.mixer.init()


# =========================
# UTILITIES
# =========================

def play_sound_popup(title="Time Alert"):
    try:
        if os.path.exists(RINGTONE_PATH):
            pygame.mixer.music.load(RINGTONE_PATH)
            pygame.mixer.music.play(-1)
        else:
            print("[TIME ERROR] alarm.mp3 not found:", RINGTONE_PATH)

        root = tk.Tk()
        root.title(title)
        root.geometry("380x200")
        root.configure(bg="#1e1e1e")
        root.resizable(False, False)

        root.update_idletasks()
        width = 380
        height = 200
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f"{width}x{height}+{x}+{y}")

        root.attributes("-topmost", True)
        root.after(100, lambda: root.attributes("-topmost", False))
        root.lift()
        root.focus_force()

        title_label = tk.Label(
            root,
            text=title,
            font=("Segoe UI", 18, "bold"),
            fg="white",
            bg="#1e1e1e"
        )
        title_label.pack(pady=30)

        def stop():
            try:
                pygame.mixer.music.stop()
            except:
                pass
            root.destroy()

        stop_button = tk.Button(
            root,
            text="STOP",
            font=("Segoe UI", 12, "bold"),
            bg="#ff4c4c",
            fg="white",
            activebackground="#ff1a1a",
            activeforeground="white",
            width=12,
            bd=0,
            command=stop
        )
        stop_button.pack(pady=20)

        root.mainloop()

    except Exception as e:
        print("[TIME ERROR - play_sound_popup]", e)


def parse_duration(command):
    command = command.lower()
    total_seconds = 0

    patterns = [
        (r'(\d+)\s*(hour|hours|hr|hrs|h)', 3600),
        (r'(\d+)\s*(minute|minutes|min|mins|m)', 60),
        (r'(\d+)\s*(second|seconds|sec|secs|s)', 1),
    ]

    for pattern, multiplier in patterns:
        matches = re.findall(pattern, command)
        for match in matches:
            total_seconds += int(match[0]) * multiplier

    return total_seconds


def parse_alarm_time(command):
    now = datetime.now()
    command = command.lower().strip()

    # Case 1: 14:30 / 09:45 / 7:15 pm
    match = re.search(r'(\d{1,2}):(\d{2})\s*(am|pm)?', command)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))
        am_pm = match.group(3)

    # Case 2: 7 am / 11 pm
    else:
        match = re.search(r'(\d{1,2})\s*(am|pm)', command)
        if not match:
            return None

        hour = int(match.group(1))
        minute = 0
        am_pm = match.group(2)

    # Convert AM/PM
    if am_pm:
        if am_pm == "pm" and hour != 12:
            hour += 12
        if am_pm == "am" and hour == 12:
            hour = 0

    # Validate hour/minute
    if hour < 0 or hour > 23 or minute < 0 or minute > 59:
        return None

    alarm_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    if alarm_time <= now:
        alarm_time += timedelta(days=1)

    return alarm_time


# =========================
# TIMER CLASS
# =========================

class Timer:
    def __init__(self, seconds, manager):
        self.seconds = seconds
        self.start_time = time.time()
        self.manager = manager
        self.active = True
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def run(self):
        time.sleep(self.seconds)
        if self.active:
            play_sound_popup("Timer Finished")
            self.manager.remove_timer(self)

    def cancel(self):
        self.active = False

    def remaining_seconds(self):
        elapsed = time.time() - self.start_time
        remaining = max(0, int(self.seconds - elapsed))
        return remaining


# =========================
# ALARM CLASS
# =========================

class Alarm:
    def __init__(self, alarm_time, manager, recurring=False):
        self.alarm_time = alarm_time
        self.manager = manager
        self.recurring = recurring
        self.active = True
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def run(self):
        while self.active:
            wait = (self.alarm_time - datetime.now()).total_seconds()
            if wait > 0:
                time.sleep(wait)

            if self.active:
                play_sound_popup("Alarm Ringing")

                if self.recurring:
                    self.alarm_time += timedelta(days=1)
                else:
                    self.manager.remove_alarm(self)
                    break

    def cancel(self):
        self.active = False


# =========================
# STOPWATCH CLASS
# =========================

class Stopwatch:
    def __init__(self):
        self.running = False
        self.start_time = None
        self.elapsed = 0

    def start(self):
        if not self.running:
            self.running = True
            self.start_time = time.time()
            return "Stopwatch started"
        return "Stopwatch already running"

    def stop(self):
        if self.running:
            self.running = False
            self.elapsed += time.time() - self.start_time
            return f"Stopwatch stopped at {round(self.elapsed, 2)} seconds"
        return "Stopwatch not running"

    def reset(self):
        self.running = False
        self.elapsed = 0
        self.start_time = None
        return "Stopwatch reset"

    def current_time(self):
        if self.running:
            return self.elapsed + (time.time() - self.start_time)
        return self.elapsed


# =========================
# TIME MANAGER
# =========================

class TimeManager:
    def __init__(self):
        self.timers = []
        self.alarms = []
        self.stopwatch = Stopwatch()

    # -------- TIMER --------
    def create_timer(self, seconds):
        timer = Timer(seconds, self)
        self.timers.append(timer)
        return f"Timer set for {seconds} seconds"

    def remove_timer(self, timer):
        if timer in self.timers:
            self.timers.remove(timer)

    def cancel_all_timers(self):
        for t in self.timers:
            t.cancel()
        self.timers.clear()
        return "All timers cancelled"

    # -------- ALARM --------
    def create_alarm(self, alarm_time, recurring=False):
        alarm = Alarm(alarm_time, self, recurring)
        self.alarms.append(alarm)
        return f"Alarm set for {alarm_time.strftime('%I:%M %p')}"

    def remove_alarm(self, alarm):
        if alarm in self.alarms:
            self.alarms.remove(alarm)

    def cancel_all_alarms(self):
        for a in self.alarms:
            a.cancel()
        self.alarms.clear()
        return "All alarms cancelled"

    # -------- LIST --------
    def list_alarms(self):
        if not self.alarms:
            return "No active alarms"

        response = "Active alarms:\n"
        for i, alarm in enumerate(self.alarms, 1):
            response += f"{i}. {alarm.alarm_time.strftime('%I:%M %p')}\n"
        return response.strip()

    def list_timers(self):
        if not self.timers:
            return "No active timers"

        response = "Active timers:\n"
        for i, timer in enumerate(self.timers, 1):
            response += f"{i}. {timer.remaining_seconds()} seconds remaining\n"
        return response.strip()

    def list_active(self):
        return f"Active timers: {len(self.timers)} | Active alarms: {len(self.alarms)}"

    # -------- STOPWATCH --------
    def handle_stopwatch(self, command):
        if "start" in command:
            return self.stopwatch.start()
        if "stop" in command:
            return self.stopwatch.stop()
        if "reset" in command:
            return self.stopwatch.reset()
        if "show" in command or "time" in command or "status" in command:
            return f"Stopwatch: {round(self.stopwatch.current_time(), 2)} seconds"
        return None


# =========================
# GLOBAL INSTANCE
# =========================

time_manager = TimeManager()


# =========================
# COMMAND HANDLER
# =========================

def handle_time_command(command: str):
    command = command.lower().strip()

    # ---------------- CANCEL FIRST ----------------
    if "cancel" in command:
        if "timer" in command:
            return time_manager.cancel_all_timers()
        if "alarm" in command:
            return time_manager.cancel_all_alarms()

    # ---------------- LIST ----------------
    if "show" in command or "list" in command:
        if "alarm" in command:
            return time_manager.list_alarms()
        if "timer" in command:
            return time_manager.list_timers()
        if "active" in command:
            return time_manager.list_active()

    # ---------------- TIMER ----------------
    if "timer" in command:
        seconds = parse_duration(command)
        if seconds > 0:
            return time_manager.create_timer(seconds)
        return "Invalid timer duration"

    # ---------------- ALARM ----------------
    if "alarm" in command or "wake me" in command:
        alarm_time = parse_alarm_time(command)
        if alarm_time:
            recurring = "daily" in command or "every day" in command
            return time_manager.create_alarm(alarm_time, recurring)
        return "Invalid alarm format. Say something like 7 AM, 7:30 PM, or 14:30"

    # ---------------- STOPWATCH ----------------
    if command == "stop" and time_manager.stopwatch.running:
        return time_manager.stopwatch.stop()

    if "stopwatch" in command:
        return time_manager.handle_stopwatch(command)

    return None