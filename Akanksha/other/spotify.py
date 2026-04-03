import os
import time
import pyautogui
import pyttsx3

pyautogui.FAILSAFE = False

engine = pyttsx3.init()

def speak(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()

# ---------------- PLAY SONG BY NAME ----------------
 
def play_song(song):
    speak(f"Playing {song}")

    os.startfile("spotify:")
    time.sleep(6)

    # Focus search
    pyautogui.hotkey("ctrl", "l")
    time.sleep(1)

    # Clear
    pyautogui.hotkey("ctrl", "a")
    pyautogui.press("backspace")

    # Type song
    pyautogui.write(song, interval=0.1)
    time.sleep(1)

    # Search
    pyautogui.press("enter")
    time.sleep(4)

    # Move into results
    pyautogui.press("tab")
    time.sleep(0.5)
    pyautogui.press("tab")
    time.sleep(0.5)

    # FORCE PLAY (this is the key)
    pyautogui.press("enter")
    time.sleep(0.5)
    pyautogui.press("enter")
    time.sleep(0.5)
    pyautogui.press("space")

# ---------------- MEDIA CONTROLS ----------------

def pause_music():
    pyautogui.press("playpause")
    speak("Paused")

def resume_music():
    pyautogui.press("playpause")
    speak("Resumed")

def next_track():
    pyautogui.press("nexttrack")
    speak("Next song")

def previous_track():
    pyautogui.press("prevtrack")
    speak("Previous song")

def volume_up():
    pyautogui.press("volumeup")
    speak("Volume up")

def volume_down():
    pyautogui.press("volumedown")
    speak("Volume down")

def mute_audio():
    pyautogui.press("volumemute")
    speak("Muted")

def unmute_audio():
    pyautogui.press("volumemute")
    speak("Unmuted")

# ---------------- COMMAND HANDLER ----------------

def handle_command(cmd):
    cmd = cmd.lower().strip()

    if cmd.startswith("play "):
        song = cmd.replace("play ", "").strip()
        if song:
            play_song(song)
        return

    if cmd == "play":
        resume_music()
        return

    if cmd == "pause":
        pause_music()
        return

    if cmd == "resume":
        resume_music()
        return

    if cmd == "next":
        next_track()
        return

    if cmd == "previous":
        previous_track()
        return

    if cmd == "volume up":
        volume_up()
        return

    if cmd == "volume down":
        volume_down()
        return

    if cmd == "mute":
        mute_audio()
        return

    if cmd == "unmute":
        unmute_audio()
        return

    speak("Command not recognized")

# ---------------- MAIN LOOP ----------------

if __name__ == "__main__":
    speak("Assistant started")

    while True:
        text = input("You: ")

        if text == "exit":
            break

        handle_command(text)