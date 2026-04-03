from engines.reminder_engine import handle_reminder_command
from engines.task_engine import handle_task_command
from engines.volume_control import handle_volume_command
from engines.brightness_control import handle_brightness_command
from engines.system_engine import handle_system_command
from engines.power_engine import handle_power_command
from engines.history_engine import (
    log_command,
    handle_history_command,
    handle_delete_history,
)
from engines.time_engine import handle_time_command
from engines.night_mode_control import handle_night_mode_command


def execute_command(command: str):
    command = command.lower().strip()

    # ---------------- TIME COMMANDS ----------------
    result = handle_time_command(command)
    if result:
        log_command(command)
        return result

    # ---------------- BRIGHTNESS ----------------
    result = handle_brightness_command(command)
    if result and result != "Brightness command not understood":
        log_command(command)
        return result

    # ---------------- VOLUME ----------------
    result = handle_volume_command(command)
    if result and result != "Volume command not understood":
        log_command(command)
        return result

    # ---------------- NIGHT MODE ----------------
    result = handle_night_mode_command(command)
    if result:
        log_command(command)
        return result

    # ---------------- SYSTEM ----------------
    result = handle_system_command(command)
    if result:
        log_command(command)
        return result

    # ---------------- POWER ----------------
    result = handle_power_command(command)
    if result:
        log_command(command)
        return result

    # ---------------- DELETE HISTORY ----------------
    delete_result = handle_delete_history(command)
    if delete_result:
        return delete_result

    # ---------------- SHOW HISTORY ----------------
    history_result = handle_history_command(command)
    if history_result:
        return history_result

    return None


# # command_engine.py
# from unittest import result



# from volume_control import handle_volume_command
# from brightness_control import handle_brightness_command
# # from night_mode_control import turn_on_night_mode, turn_off_night_mode
# from system_engine import handle_system_command
# from power_engine import handle_power_command
# from history_engine import (
#     log_command,
#     handle_history_command,
#     handle_delete_history,
#     load_history
# )
# from time_engine import handle_time_command
# # from calendar_engine import handle_calendar_command




# def execute_command(command: str):
#     command = command.lower()

#     # ---------------------------------
#     # ROUTING LAYER (DOMAIN DETECTION)
#     # ---------------------------------



#     # ---------------- TIME COMMANDS ----------------
#     result = handle_time_command(command)
#     if result:
#         log_command(command)
#         return result
    
#     # ---------------- CALENDAR ----------------
#     # result = handle_calendar_command(command)
#     # if result:
#     #     log_command(command)
#     #     return result
    
#     # Brightness commands
#     if any(word in command for word in ["brightness", "screen", "display"]):
#         result = handle_brightness_command(command)
#         if result:
#             log_command(command)
#             return result
        
#     # Volume commands
#     if any(word in command for word in ["volume", "sound", "audio", "mute"]):
#         result = handle_volume_command(command)
#         if result:
#             log_command(command)
#             return result
        
#     # night mode commands can be added here in the future

#     # system commands should  
#     result = handle_system_command(command)
#     if result:
#         log_command(command)
#         return result
    
#     # power commands
#     result = handle_power_command(command)
#     if result:
#         log_command(command)
#         return result
    
#       # ---------------- DELETE HISTORY ----------------
#     delete_result = handle_delete_history(command)
#     if delete_result:
#         return delete_result

#     # ---------------- SHOW HISTORY ----------------
#     history_result = handle_history_command(command)
#     if history_result:
#         return history_result
    
    
    
#     #ENDPOINT 
#     return "Command not recognized"