import subprocess
import re

pending_action = None


# ==========================================
# EXECUTE ACTION
# ==========================================

def execute_action(action, delay=0):

    if action == "shutdown":
        subprocess.Popen(f"shutdown /s /t {delay}", shell=True)
        return f"Shutdown scheduled in {delay} seconds"

    elif action == "restart":
        subprocess.Popen(f"shutdown /r /t {delay}", shell=True)
        return f"Restart scheduled in {delay} seconds"

    elif action == "lock":
        subprocess.Popen("rundll32.exe user32.dll,LockWorkStation", shell=True)
        return "System locked"

    elif action == "sleep":
        subprocess.Popen("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
        return "System entering sleep mode"

    return None


# ==========================================
# CANCEL SHUTDOWN
# ==========================================

def cancel_shutdown():
    subprocess.Popen("shutdown /a", shell=True)
    return "Shutdown or restart cancelled"


# ==========================================
# POWER COMMAND HANDLER
# ==========================================

def handle_power_command(command: str):
    global pending_action

    command = command.lower().strip()

    # ======================================
    # CANCEL SHUTDOWN / RESTART ONLY
    # ======================================

    if re.search(r'\b(cancel|abort|undo)\b', command) and \
       re.search(r'\b(shutdown|restart|reboot)\b', command):
        return cancel_shutdown()

    # ======================================
    # TIME DELAY PARSING
    # ======================================

    delay = 0
    time_match = re.search(r'(\d+)\s*(sec|second|seconds|min|mins|minute|minutes)', command)

    if time_match:
        value = int(time_match.group(1))
        unit = time_match.group(2)

        if "minute" in unit:
            delay = value * 60
        else:
            delay = value

    # ======================================
    # SHUTDOWN
    # ======================================

    if re.search(r'\bshutdown\b', command) or \
       re.search(r'\bshut down\b', command) or \
       re.search(r'\bturn off\b', command):

        if delay > 0:
            return execute_action("shutdown", delay)

        pending_action = "shutdown"
        return "Are you sure you want to shutdown? (yes/no)"

    # ======================================
    # RESTART
    # ======================================

    if re.search(r'\b(restart|reboot)\b', command):

        if delay > 0:
            return execute_action("restart", delay)

        pending_action = "restart"
        return "Are you sure you want to restart? (yes/no)"

    # ======================================
    # LOCK
    # ======================================

    if re.search(r'\block\b', command):
        return execute_action("lock")

    # ======================================
    # SLEEP
    # ======================================

    if re.search(r'\bsleep\b', command):
        return execute_action("sleep")

    # ======================================
    # CONFIRMATION
    # ======================================

    if command == "yes" and pending_action:
        action = pending_action
        pending_action = None
        return execute_action(action, 6)  # 6-second undo window

    if command == "no" and pending_action:
        pending_action = None
        return "Action cancelled"

    return None