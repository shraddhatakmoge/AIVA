import pyautogui
import time

print("Tracking mouse... Press Ctrl+C to stop.")
try:
    while True:
        x, y = pyautogui.position()
        print(f"X: {x} | Y: {y}", end="\r")
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nDone.")

    
