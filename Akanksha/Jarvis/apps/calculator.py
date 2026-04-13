import os
import subprocess
import time
import pyautogui
import pygetwindow as gw
import re

# ==============================
# 🚀 APP LAUNCHER: CALCULATOR
# ==============================

def open_calculator():
    print("Opening calculator")
    try:
        subprocess.Popen("calc.exe")
        time.sleep(1.5)  # Give Windows time to open the app
        # print("✅ Opened Calculator")
    except Exception as e:
        print(f"I encountered an error trying to bring Calculator to the front")

def close_calculator():
    response = os.system("taskkill /f /im CalculatorApp.exe >nul 2>&1")
    if response == 0:
        print("✅ Closed Calculator")
    else:
        print("❌ Calculator was not running")

# ==============================
# 🪟 WINDOW MANAGER
# ==============================

def ensure_calculator_active():
    """Finds the calculator window and brings it to the front."""
    try:
        # Look for a window with "Calculator" in the title
        calc_windows = gw.getWindowsWithTitle("Calculator")
        if calc_windows:
            win = calc_windows[0]
            # If minimized, restore it
            if win.isMinimized:
                win.restore()
            # Bring to front
            win.activate()
            time.sleep(0.5)
            return True
    except Exception as e:
        print(f"I encountered an error trying to bring Calculator to the front")
    return False

# ==============================
# 🧮 MATH AUTOMATION
# ==============================

def calculate(original_command, expression):
    if not ensure_calculator_active():
        open_calculator()
        ensure_calculator_active()

    # ==============================
    # 🧠 SMART CHAINING LOGIC
    # ==============================
    is_chaining = False
    
    # 1. If basic math starts with a symbol (e.g., "+ 5", "* 10")
    if expression and expression[0] in ['+', '-', '*', '/']:
        is_chaining = True
        
    # 2. If advanced math has NO numbers (e.g., "square" instead of "square of 5")
    numbers = re.findall(r'\d+', original_command)
    if not expression and len(numbers) == 0:
        is_chaining = True

    # Only press Esc if we are starting a brand new calculation
    if not is_chaining:
        pyautogui.press('esc')
        time.sleep(0.2)

    # ==============================
    # 1️⃣ BASIC MATH
    # ==============================
    if expression:
        pyautogui.write(expression, interval=0.1)
        time.sleep(0.2)
        pyautogui.press('enter')
        print("✅ Basic math completed!")
        return

    # ==============================
    # 2️⃣ ADVANCED MATH
    # ==============================
    else:
        
        # Find all numbers in the user's spoken command
        numbers = re.findall(r'\d+', original_command)
        num1 = numbers[0] if len(numbers) > 0 else ""
        num2 = numbers[1] if len(numbers) > 1 else ""

        # PI
        if "pi" in original_command:
            pyautogui.press('p')  # Shortcut for Pi
            
        # SQUARE ROOT (e.g., "square root of 144")
        elif "square root" in original_command or "root" in original_command:
            if num1:
                pyautogui.write(num1, interval=0.1)
                time.sleep(0.2)             # Give UI a split second to catch up
                pyautogui.write('@')        # Use write() instead of press() for symbols
                time.sleep(0.2)
                pyautogui.press('enter')    # Force the equals button
                
        # SQUARE (e.g., "square of 5")
        elif "square" in original_command:
            if num1:
                pyautogui.write(num1, interval=0.1)
                time.sleep(0.2)             # Give UI a split second to catch up
                pyautogui.write('q')        # Use write() instead of press() for letters
                time.sleep(0.2)
                pyautogui.press('enter')    # Force the equals button

        # FACTORIAL (e.g., "factorial of 5")
        elif "factorial" in original_command:
            if num1:
                pyautogui.hotkey('alt', '2')  # Switch to Scientific Mode
                time.sleep(0.4)               # Wait a split second for the UI to change
                
                pyautogui.write(num1, interval=0.1)
                pyautogui.write('!')          # write() handles symbols much better than press()
                
                time.sleep(0.8)               # Let the user see the answer
                

        # POWER (e.g., "5 to the power of 3")
        elif "power" in original_command:
            if num1 and num2:
                pyautogui.write(num1, interval=0.1)
                pyautogui.press('^')  # Shortcut for power
                pyautogui.write(num2, interval=0.1)
                pyautogui.press('enter')
        
        else:
            print("❌ Advanced math command not fully understood.")
            return

        print("✅ Advanced math completed on screen!")