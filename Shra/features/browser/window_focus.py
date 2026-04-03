import win32gui
import win32con
import win32process
import psutil
import time


def bring_browser_to_front():
    time.sleep(0.3)

    def enum_handler(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "Chrome" in title:
                try:
                    # Restore if minimized
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

                    # Force foreground
                    win32gui.SetForegroundWindow(hwnd)

                    # Force focus trick
                    win32gui.BringWindowToTop(hwnd)
                    win32gui.SetActiveWindow(hwnd)
                except:
                    pass

    win32gui.EnumWindows(enum_handler, None)