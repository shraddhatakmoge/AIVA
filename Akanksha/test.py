# import pyautogui
# import time

# print("Tracking mouse... Press Ctrl+C to stop.")
# try:
#     while True:
#         x, y = pyautogui.position()
#         print(f"X: {x} | Y: {y}", end="\r")
#         time.sleep(0.1)
# except KeyboardInterrupt:
#     print("\nDone.")

import os
import time
import pyautogui

print("Test: Trying to open Word...")
os.startfile("winword")
time.sleep(5)
pyautogui.press('enter')
print("Test: Did it work?")
