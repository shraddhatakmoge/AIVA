import pyautogui
import time

def type_text(text):
    time.sleep(3)  # wait for app to open

    # Force switch to latest opened window
    pyautogui.keyDown("alt")
    pyautogui.press("tab")
    pyautogui.keyUp("alt")

    time.sleep(1)

    pyautogui.write(text, interval=0.05)