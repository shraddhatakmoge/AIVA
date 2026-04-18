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
    """
    Universal Open: Uses Windows URI to launch Spotify without hardcoded paths.
    """
    print(" Attempting to launch Spotify...")
    
    # 1. THE UNIVERSAL WAY: URI Scheme works for all installations
    # This replaces looking for specific AppData folders.
    os.system("start spotify:") 
    
    # 2. WAIT FOR INITIALIZATION
    # Give it 4 seconds—essential for slower laptops to load the UI.
    time.sleep(4) 
    
    # 3. FOCUS VERIFICATION
    # Use your existing focus function to ensure it's at the front.
    if not focus_spotify():
        # Fallback: If URI failed, use the Start Menu search
        pyautogui.press("win")
        time.sleep(0.5)
        pyautogui.write("spotify", interval=0.05)
        time.sleep(0.8)
        pyautogui.press("enter")
    
    # Only one message at the end
    # print("Spotify opened")

# ---------------- CLOSE ----------------
def close_spotify():
    print("Closing Spotify")
    # Notice the /t added right after Spotify.exe !
    os.system("taskkill /f /im Spotify.exe /t >nul 2>&1")
    # print("✅ Spotify closed")

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
    # 🔥 THE FIX: Strip 'on spotify' from the query before typing
    clean_query = song.lower().replace("on spotify", "").strip()
    
    pyautogui.hotkey("ctrl", "l") # Standard shortcut to focus search
    time.sleep(1)

    pyautogui.hotkey("ctrl", "a")
    pyautogui.press("backspace")

    pyautogui.write(clean_query, interval=0.07)
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
    
    pyautogui.press("tab")
    pyautogui.press("tab")
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
    """
    Robust Portable Version: Forces a 'Physical' key hold instead of coordinates.
    """
    print("Attempting to like current track...")
    
    # Use your existing focus function to bring Spotify to the front
    if not focus_spotify():
        # Use your portable open function if it's not open
        open_spotify()
        time.sleep(2)
        focus_spotify()

    # Give Windows a moment to stabilize focus
    time.sleep(1)

    # 🔥 THE ROBUST SEQUENCE: Manually holding keys
    # This replaces the need for x, y = 1854, 839
    pyautogui.keyDown('alt')
    pyautogui.keyDown('shift')
    pyautogui.press('b')
    time.sleep(0.2)
    pyautogui.keyUp('shift')
    pyautogui.keyUp('alt')
    
    print("Song added to Liked Songs ")