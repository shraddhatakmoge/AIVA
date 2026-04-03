# import os
# import time
# import keyboard
# import pyautogui

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# def toggle_night_mode():
#     keyboard.press_and_release("win+a")
#     time.sleep(1)

#     tile_path = os.path.join(BASE_DIR, "night_tile.png")

#     location = pyautogui.locateOnScreen(
#         tile_path,
#         confidence=0.8
#     )

#     if location:
#         center = pyautogui.center(location)
#         pyautogui.moveTo(center.x, center.y, duration=0.3)
#         pyautogui.click()
#         result = "Night mode toggled"
#     else:
#         result = "Night Light tile not found"

#     time.sleep(0.5)
#     keyboard.press_and_release("win+a")

#     return result


# def turn_on_night_mode():
#     return toggle_night_mode()


# def turn_off_night_mode():
#     return toggle_night_mode()



import os
import time
import keyboard
import pyautogui

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TILE_PATH = os.path.join(os.path.dirname(BASE_DIR), "assets", "images", "night_tile.png")


def toggle_night_mode():
    keyboard.press_and_release("win+a")
    time.sleep(1)

    location = pyautogui.locateOnScreen(TILE_PATH, confidence=0.8)

    if location:
        center = pyautogui.center(location)
        pyautogui.moveTo(center.x, center.y, duration=0.3)
        pyautogui.click()
        result = "Night light toggled"
    else:
        result = "Night light tile not found"

    time.sleep(0.5)
    keyboard.press_and_release("win+a")
    return result


def handle_night_mode_command(command: str):
    command = command.lower().strip()

    keywords = ["night light", "night mode", "blue light", "eye comfort"]

    if not any(k in command for k in keywords):
        return None

    if "turn on" in command or "enable" in command or "start" in command:
        return toggle_night_mode()

    if "turn off" in command or "disable" in command or "stop" in command:
        return toggle_night_mode()

    if "toggle" in command:
        return toggle_night_mode()

    return "Night light command not understood"