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