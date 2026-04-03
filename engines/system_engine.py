# system_engine.py

import psutil


def format_bytes(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024


def handle_system_command(command: str):
    command = command.lower()

    # Block non-system actions
    block_words = ["install", "download", "open", "close", "delete"]
    if any(word in command for word in block_words):
        return None

    system_keywords = [
        "cpu", "processor",
        "ram", "memory",
        "disk", "storage",
        "battery",
        "network", "internet", "wifi"
    ]

    if not any(word in command for word in system_keywords):
        return None

    response = []

    # CPU
    if "cpu" in command or "processor" in command:
        usage = psutil.cpu_percent(interval=1)
        cores = psutil.cpu_count()
        response.append(f"CPU: {usage}% | Cores: {cores}")

    # RAM
    if "ram" in command or "memory" in command:
        mem = psutil.virtual_memory()
        response.append(
            f"RAM: {mem.percent}% | Used: {format_bytes(mem.used)} / {format_bytes(mem.total)}"
        )

    # Disk
    if "disk" in command or "storage" in command:
        disk = psutil.disk_usage('/')
        response.append(
            f"Disk: {disk.percent}% | Used: {format_bytes(disk.used)} / {format_bytes(disk.total)}"
        )

    # Battery
    if "battery" in command:
        battery = psutil.sensors_battery()
        if battery:
            response.append(
                f"Battery: {battery.percent}% | Charging: {battery.power_plugged}"
            )
        else:
            response.append("Battery info not available")

    # Network
    if "network" in command or "internet" in command or "wifi" in command:
        net = psutil.net_io_counters()
        response.append(
            f"Network: Sent {format_bytes(net.bytes_sent)} | Received {format_bytes(net.bytes_recv)}"
        )

    if response:
        return " | ".join(response)

    return None