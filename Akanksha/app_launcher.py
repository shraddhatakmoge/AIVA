import os
import subprocess
import time
import pyautogui
import pyttsx3
import pygetwindow as gw

# ---------------- TEXT TO SPEECH ----------------

engine = pyttsx3.init()

def speak(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()

# ---------------- DESKTOP APPS ----------------

DESKTOP_APPS = {
    "notepad": "notepad",
    "calculator": "calc",
    "vscode": "code",
    "explorer": "explorer",
    "paint": "mspaint",
    "cmd": "cmd"
}

def pause_music():
    speak("Music paused")
    pyautogui.press("playpause")

def resume_music():
    speak("Music resumed")
    pyautogui.press("playpause")



def volume_up():
    speak("Volume up")
    pyautogui.press("volumeup")

def volume_down():
    speak("Volume down")
    pyautogui.press("volumedown")

def next_track():
    speak("Next track")
    pyautogui.press("nexttrack")

def previous_track():
    speak("Previous track")
    pyautogui.press("prevtrack")

def mute_audio():
    speak("Audio muted")
    pyautogui.press("volumemute")

def unmute_audio():
    speak("Audio unmuted")
    pyautogui.press("volumemute")   # same key toggles mute


# ---------------- SPOTIFY CONTROL ----------------

def focus_spotify():
    try:
        windows = gw.getWindowsWithTitle("Spotify")
        if windows:
            windows[0].activate()
            time.sleep(1)
    except:
        pass

def play_song(song):

    speak(f"Playing {song}")

    # Open Spotify search
    os.startfile(f"spotify:search:{song}")

    time.sleep(7)

    focus_spotify()

    # Single play trigger
    pyautogui.press("space")

def open_spotify():
    speak("Opening Spotify")
    os.startfile("spotify:")

# ---------------- COMMAND HANDLER ----------------

def handle_command(cmd):

    cmd = cmd.strip()



    if cmd.startswith("play"):
        song = cmd.replace("play","").strip()
        if song:
            play_song(song)
        else:
            speak("Please say the song name")
        return

    if "pause" in cmd:
        pause_music()
        return

    if "resume" in cmd or "play music" in cmd:
        resume_music()
        return

    if "volume up" in cmd:
        volume_up()
        return

    if "volume down" in cmd:
        volume_down()
        return
    
    

    if "open spotify" in cmd:
     open_spotify()
    return



# ---------------- MAIN LOOP ----------------

speak("Accessibility assistant started")

while True:

    user = input("You: ").lower()

    if user == "exit":
        speak("Goodbye")
        break

    for part in user.split("and"):
        handle_command(part)
