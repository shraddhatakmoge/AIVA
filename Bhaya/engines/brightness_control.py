import re
import wmi


class BrightnessController:
    def __init__(self):
        pass

    def set_brightness(self, value):
        try:
            value = max(0, min(100, int(value)))

            # Create WMI object fresh inside the same thread
            w = wmi.WMI(namespace='wmi')
            methods = w.WmiMonitorBrightnessMethods()

            if not methods:
                return "Brightness control is not supported on this device"

            methods[0].WmiSetBrightness(value, 0)
            return f"Brightness set to {value}%"

        except Exception as e:
            print("[BRIGHTNESS ERROR - set_brightness]", e)
            return "Failed to change brightness"

    def get_brightness(self):
        try:
            # Create WMI object fresh inside the same thread
            w = wmi.WMI(namespace='wmi')
            brightness = w.WmiMonitorBrightness()

            if not brightness:
                return "Brightness info is not available"

            level = brightness[0].CurrentBrightness
            return f"Current brightness is {level}%"

        except Exception as e:
            print("[BRIGHTNESS ERROR - get_brightness]", e)
            return "Failed to get brightness level"


brightness = BrightnessController()


def handle_brightness_command(command: str):
    command = command.lower().strip()

    if "brightness" not in command:
        return None

    if "what" in command or "current" in command or "show" in command:
        return brightness.get_brightness()

    if "max" in command or "maximum" in command or "full" in command:
        return brightness.set_brightness(100)

    if "min" in command or "minimum" in command or "lowest" in command:
        return brightness.set_brightness(0)

    number_match = re.search(r'(\d+)', command)
    if number_match:
        number = int(number_match.group(1))
        return brightness.set_brightness(number)

    if "increase" in command or "up" in command:
        current = brightness.get_brightness()
        match = re.search(r'(\d+)', current)
        if match:
            new_value = int(match.group(1)) + 10
            return brightness.set_brightness(new_value)

    if "decrease" in command or "down" in command or "reduce" in command:
        current = brightness.get_brightness()
        match = re.search(r'(\d+)', current)
        if match:
            new_value = int(match.group(1)) - 10
            return brightness.set_brightness(new_value)

    return "Brightness command not understood"