import os
import time
import pyautogui
import pygetwindow as gw
import subprocess

# ---------------- FOCUS ----------------
def focus_spotify():
    windows = gw.getWindowsWithTitle("Spotify")

    if not windows:
        return False

    try:
        win = windows[0]

        if win.isMinimized:
            win.restore()
            time.sleep(1)

        win.activate()
        time.sleep(1)
        return True

    except:
        return False


# ---------------- OPEN ----------------
def open_spotify():
    standard_path = os.path.expanduser("~\\AppData\\Roaming\\Spotify\\Spotify.exe")
    store_path = os.path.expanduser("~\\AppData\\Local\\Microsoft\\WindowsApps\\Spotify.exe")
    
    # 1. Try Direct App Paths First
    if os.path.exists(standard_path):
        subprocess.Popen(standard_path)
    elif os.path.exists(store_path):
        subprocess.Popen(store_path)
    else:
        # 2. Try URI Scheme
        os.system("start spotify:")
        time.sleep(2)
        
        # 3. Final Fallback: Keyboard Search
        pyautogui.press("win")
        time.sleep(0.5)
        pyautogui.write("spotify", interval=0.05) 
        time.sleep(0.5)
        pyautogui.press("enter")
        
    # Only print one single message at the very end!
    print("✅ Spotify opened")

# ---------------- CLOSE ----------------
def close_spotify():
    # Notice the /t added right after Spotify.exe !
    os.system("taskkill /f /im Spotify.exe /t >nul 2>&1")
    print("✅ Spotify closed")

# ---------------- PLAY SONG ----------------
def play_song(song):
    # 1. Open Spotify
    open_spotify()
    
    # 2. 🔥 CRITICAL PAUSE: Give Spotify 4 seconds to actually appear on screen
    time.sleep(4)
    
    # 3. 🔥 BRING TO FRONT: Switch away from the terminal!
    focus_spotify()
    
    # 4. Now that Spotify is guaranteed to be in front, we can press Ctrl+L
    search_song(song)
    click_first_result()
    
# --------- SEARCH SONG ---------
def search_song(song):
    pyautogui.hotkey("ctrl", "l")
    time.sleep(1)

    pyautogui.hotkey("ctrl", "a")
    pyautogui.press("backspace")

    pyautogui.write(song, interval=0.07)
    time.sleep(1)

    pyautogui.press("enter")
    time.sleep(3)

def click_first_result():
    x, y = 509, 203   # 🔥 your coordinates

       # 🎯 MOVE TO COORDINATES
    pyautogui.moveTo(x, y, duration=0.3)

    time.sleep(0.5)  # 🔥 VERY IMPORTANT

    # 🔥 STRONG CLICK
    pyautogui.click(x, y)
    time.sleep(0.2)
    pyautogui.click(x, y)   # double click (ensures selection)

    # 🔥 OPTIONAL: press enter to force play
    pyautogui.press("enter")
    
# ---------------- CONTROLS ----------------
def pause_music():
    pyautogui.press("playpause")
    print("⏸️ Paused")


def resume_music():
    pyautogui.press("playpause")
    print("▶️ Resumed")


def next_track():
    pyautogui.press("nexttrack")
    print("⏭️ Next song")


def previous_track():
    pyautogui.press("prevtrack")
    print("⏮️ Previous song")
    
def like_song():
  

    # 🔥 Step 1: Open Spotify
    os.system("start shell:AppsFolder\\SpotifyAB.SpotifyMusic_zpdnekdrzrea0!Spotify")
    time.sleep(5)

    # 🔥 Step 2: Focus Spotify window
    windows = gw.getWindowsWithTitle("Spotify")
    if windows:
        try:
            win = windows[0]

            if win.isMinimized:
                win.restore()
                time.sleep(1)

            win.activate()
            time.sleep(1)

        except:
            print("⚠️ Could not focus Spotify")

    # 🔥 Step 3: Move to heart button
    x, y = 1854, 839   # your coordinates

    pyautogui.moveTo(x, y, duration=0.3)
    time.sleep(0.5)

    # 🔥 Step 4: Click (double for safety)
    pyautogui.click()
    time.sleep(0.2)
    pyautogui.click()

    print("✅ Song added to Liked Songs")