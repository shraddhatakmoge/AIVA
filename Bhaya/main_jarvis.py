

import os
print("RUNNING THIS FILE:", os.path.abspath(__file__))
print("HELLO MAIN STARTED")

print("IMPORTING sys...")
import sys
print("OK sys")

print("IMPORTING time...")
import time
print("OK time")

print("IMPORTING traceback...")
import traceback
print("OK traceback")

import random

print("IMPORTING Thread...")
from threading import Thread
print("OK Thread")

print("IMPORTING QApplication...")
from PyQt6.QtWidgets import QApplication
print("OK QApplication")

print("IMPORTING JarvisUI...")
from ui.window import JarvisUI
print("OK JarvisUI")

print("IMPORTING speak...")
from core.tts import speak, stop_speaking, is_speaking
print("OK speak")

print("IMPORTING start_recorder...")
from core.audio import start_recorder
print("OK start_recorder")

print("IMPORTING wake word functions...")
from core.wake_word import init_wake_word, detect_wake_word
print("OK wake word functions")

print("IMPORTING transcribe...")
from core.speech_to_text import transcribe
print("OK transcribe")# import os
# print("RUNNING THIS FILE:", os.path.abspath(__file__))
# print("HELLO MAIN STARTED")

from engines.command_engine import execute_command
from engines.history_engine import load_history, is_waiting_for_history_confirmation
from engines.power_engine import pending_action
# import sys
# import time
# import traceback
# from threading import Thread
# from PyQt6.QtWidgets import QApplication

# from ui.window import JarvisUI
# from core.tts import speak
# from core.audio import start_recorder
# from core.wake_word import init_wake_word, detect_wake_word
# from core.speech_to_text import transcribe

print("STARTING MAIN...")


def safe_ui_update(ui, status, message):
    try:
        ui.update_ui(status, message)
        print(f"[UI] {status} - {message}")
    except Exception as e:
        print("[UI ERROR]", e)

def assistant_loop(ui):
    print("[THREAD] Assistant thread started")

    try:
        safe_ui_update(ui, "Starting", "Initializing system...")

        print("[STEP] Speaking startup message...")
        speak("System ready")

        print("[STEP] Starting recorder...")
        start_recorder()
        print("[OK] Recorder started")

        print("[STEP] Initializing wake word...")
        init_wake_word()
        print("[OK] Wake word initialized")

        load_history()
        print("[OK] History loaded")

    except Exception as e:
        print("[FATAL INIT ERROR]")
        traceback.print_exc()
        safe_ui_update(ui, "Error", f"Startup failed: {e}")
        return

    # Tracks last time user interacted
    last_interaction_time = 0

    while True:
        try:
            # ---------------- FOLLOW-UP MODE CHECK ----------------
            waiting_for_followup = (
                is_waiting_for_history_confirmation() or pending_action is not None
            )

            if waiting_for_followup:
                safe_ui_update(ui, "Follow-up", "Waiting for yes or no...")
                print("[FOLLOW-UP] Waiting directly for confirmation...")
                detected = True
            else:
                safe_ui_update(ui, "Idle", "Waiting for Jarvis")
                print("[WAITING] Listening for wake word...")
                detected = detect_wake_word()

            if not detected:
                continue

            print("[DETECTED] Triggered")

            safe_ui_update(ui, "Active", "Listening...")

            # ---------------- SMART WAKE RESPONSE ----------------
            current_time = time.time()
            time_since_last = current_time - last_interaction_time

            if time_since_last > 600:
                speak("How can I help you?")
                time.sleep(1.2)

            elif time_since_last > 30:
                speak(random.choice(["Yes?", "Hmm?", "Go ahead.", "I'm listening."]))
                time.sleep(0.8)

            else:
                print("[WAKE] Silent wake")

            # ---------------- RECORD COMMAND ----------------
            print("[STEP] Recording command...")
            command = transcribe()
            print("[RAW COMMAND]:", command)

            # ---------------- STOP COMMAND ----------------
            stop_words = [
                "stop", "stop talking", "cancel", "enough",
                "be quiet", "shut up", "okay stop",
                "that's all", "alright stop",
                "jarvis stop", "jarvis wait",
                "hold on", "pause", "wait", "quiet"
            ]

            if command and command.lower().strip() in stop_words:
                stop_speaking()
                safe_ui_update(ui, "Stopped", "Speech interrupted")
                print("[ACTION] Speech interrupted")
                continue

            # ---------------- EMPTY COMMAND ----------------
            if not command or not str(command).strip():
                safe_ui_update(ui, "Error", "Didn't understand")
                print("[FAIL] No command detected")
                speak("I did not understand. Please say it again.")
                last_interaction_time = time.time()
                continue

            command = str(command).strip()

            safe_ui_update(ui, "You said", command)
            print("[USER SAID]:", command)

            safe_ui_update(ui, "Thinking", "Processing...")
            print("[STEP] Executing command...")

            response = execute_command(command)

            if not response:
                response = "Sorry, I do not know how to do that yet."

            print("[RESPONSE]:", response)

            safe_ui_update(ui, "Speaking", response)
            speak(response)

            last_interaction_time = time.time()

        except Exception as e:
            print("[LOOP ERROR]")
            traceback.print_exc()
            safe_ui_update(ui, "Error", f"Loop error: {e}")
            speak("Something went wrong")
            time.sleep(2)

        
# def assistant_loop(ui):
#     print("[THREAD] Assistant thread started")

#     try:
#         safe_ui_update(ui, "Starting", "Initializing system...")
#         print("[STEP] Speaking startup message...")
#         speak("System ready")

#         print("[STEP] Starting recorder...")
#         start_recorder()
#         print("[OK] Recorder started")

#         print("[STEP] Initializing wake word...")
#         init_wake_word()
#         print("[OK] Wake word initialized")

#     except Exception as e:
#         print("[FATAL INIT ERROR]")
#         traceback.print_exc()
#         safe_ui_update(ui, "Error", f"Startup failed: {e}")
#         return

#     while True:
#         try:
#             safe_ui_update(ui, "Idle", "Waiting for Jarvis")
#             print("[WAITING] Listening for wake word...")

#             detect_wake_word()
#             print("[DETECTED] Wake word detected")

#             safe_ui_update(ui, "Active", "Listening...")
#             speak("How can I help you?")

#             # Prevent STT from capturing the wake word itself
#             time.sleep(1.2)

#             print("[STEP] Recording command...")
#             command = transcribe()

#             print("[RAW COMMAND]:", command)

#             if not command or not str(command).strip():
#                 safe_ui_update(ui, "Error", "Didn't understand")
#                 print("[FAIL] No command detected")
#                 speak("I did not understand. Please say it again.")
#                 continue

#             command = str(command).strip()

#             safe_ui_update(ui, "You said", command)
#             print("[USER SAID]:", command)

#             # repeat user command
#             speak(f"You said {command}")

#             time.sleep(1)

#         except Exception as e:
#             print("[LOOP ERROR]")
#             traceback.print_exc()
#             safe_ui_update(ui, "Error", f"Loop error: {e}")
#             speak("Something went wrong")
#             time.sleep(2)


# ===== APP START =====
try:
    app = QApplication(sys.argv)
    print("[OK] QApplication created")

    ui = JarvisUI()
    ui.show()
    print("[OK] UI shown")

    Thread(target=assistant_loop, args=(ui,), daemon=True).start()
    print("[OK] Assistant thread launched")

    sys.exit(app.exec())

except Exception as e:
    print("[MAIN ERROR]")
    traceback.print_exc()