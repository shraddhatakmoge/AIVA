import os
import subprocess

# -------- SEARCH APP AUTOMATICALLY --------
def find_app(exe_name):
    search_paths = [
        os.environ.get("PROGRAMFILES", ""),
        os.environ.get("PROGRAMFILES(X86)", ""),
        os.environ.get("LOCALAPPDATA", ""),
        os.environ.get("APPDATA", "")
    ]

    for base in search_paths:
        for root, dirs, files in os.walk(base):
            if exe_name in files:
                return os.path.join(root, exe_name)

    return None


# -------- OPEN APP --------
def open_app_by_name(exe_name):
    path = find_app(exe_name)

    if path:
        subprocess.Popen(path)
        print(f"✅ Opened {exe_name}")
    else:
        print(f"❌ {exe_name} not found")


# -------- SYSTEM APPS --------
def open_system_app(command):
    os.system(command)


# -------- CLOSE APP --------
def close_app(app_name):
    os.system(f"taskkill /f /im {app_name}.exe >nul 2>&1")
    
# -------- SEARCH FOR FILES (SMART PORTABLE & MULTI-MATCH) --------
def find_document(spoken_name, specific_location=None, return_all=False):
    
    # Map the spoken words to actual Windows paths (NO ONEDRIVE)
    location_map = {
        "documents": [os.path.expanduser("~\\Documents")],
        "downloads": [os.path.expanduser("~\\Downloads")],
        "desktop": [os.path.expanduser("~\\Desktop")]
    }

    # 🔥 Decide where to search based on the user's command
    if specific_location and specific_location in location_map:
        search_paths = location_map[specific_location]
        
    else:
        # Search everywhere if no location was mentioned (LOCAL ONLY)
        search_paths = [
            os.path.expanduser("~\\Documents"),
            os.path.expanduser("~\\Downloads"),
            os.path.expanduser("~\\Desktop")
        ]

    spoken_lower = spoken_name.lower().strip()
    search_words = spoken_lower.split()

    # We will store ALL matches we find in this list
    found_files = []

    # Strategy 1 & 2: Exact or Underscore matches
    for base in search_paths:
        if not os.path.exists(base):
            continue 
            
        for root, dirs, files in os.walk(base):
            for file in files:
                file_lower = file.lower()
                if spoken_lower in file_lower or spoken_lower.replace(" ", "_") in file_lower:
                    found_files.append(os.path.join(root, file))

    # Strategy 3: Fallback Keyword match (Only if we found NOTHING yet)
    if not found_files and len(search_words) > 0:
        first_word = search_words[0]
        if len(first_word) > 2:
        
            for base in search_paths:
                if not os.path.exists(base):
                    continue
                for root, dirs, files in os.walk(base):
                    for file in files:
                        if first_word in file.lower():
                            found_files.append(os.path.join(root, file))

    # Remove any accidental duplicates just to be safe
    found_files = list(set(found_files))

    # ==========================================
    # 🧠 THE SELECTION MENU (Handling the results)
    # ==========================================
    
    if len(found_files) == 0:
        print(f"❌ Could not find any file matching '{spoken_name}'")
        return None
        
    elif len(found_files) == 1:
        print(f"✅ Found exactly one match: {found_files[0]}")
        return found_files[0]
        
    else:
        # We found multiple files! Let the user choose.
        print(f"\n⚠️ Found {len(found_files)} files matching '{spoken_name}':")
        for index, path in enumerate(found_files):
            print(f"  [{index + 1}] {path}")
            
        while True:
            # .strip().lower() cleans the input so "Cancel " becomes "cancel"
            choice = input("\n👉 Enter the file number (or say 'cancel'): ").strip().lower()
            
            # 🔥 Check for natural language cancel commands
            cancel_words = ['0', 'cancel', 'stop', 'abort', 'exit', 'nevermind', 'no']
            if choice in cancel_words:
                print("❌ Attachment cancelled by user.")
                return None
                
            # If they didn't cancel, try to read it as a number
            try:
                idx = int(choice) - 1
                
                if 0 <= idx < len(found_files):
                    print(f"✅ Selected: {found_files[idx]}")
                    return found_files[idx]
                else:
                    print("❌ Invalid number. Please pick a number from the list.")
            except ValueError:
                print("❌ Please enter a valid number or say 'cancel'.")
                


# -------- SMART CONTACT RESOLVER --------
def resolve_contact(spoken_name):
    # Just clean up any extra spaces from the voice command
    clean_name = spoken_name.strip()
    
    return clean_name

import os

# -------- DEEP SYSTEM SCAN (WITH OR WITHOUT ONEDRIVE) --------
def deep_scan_document(spoken_name, include_onedrive=False):
    """
    Scans the entire User Profile instead of just 3 folders.
    Portable: Uses '~' so it works on any computer without hardcoding paths.
    """
    user_profile = os.path.expanduser("~")
    onedrive_path = os.path.join(user_profile, "OneDrive")
    
    # If you TRULY want to scan the whole C: drive, change base_path to "C:\\"
    # But user_profile is 100x faster and safer!
    base_path = user_profile 

    spoken_lower = spoken_name.lower().strip()
    found_files = []

    print(f"🔍 JARVIS: Initiating DEEP SCAN for '{spoken_name}'...")
    if not include_onedrive:
        print("🚫 JARVIS: Bypassing OneDrive...")

    # Walk through every single folder inside the base path
    for root, dirs, files in os.walk(base_path):
        
        # ⚡ SPEED OPTIMIZATION: Skip hidden app data which takes forever to scan
        if "AppData" in root or "Application Data" in root:
            continue
            
        # ☁️ ONEDRIVE FILTER: Skip OneDrive folders if the switch is False
        if not include_onedrive and onedrive_path in root:
            continue

        # Look for the file
        for file in files:
            if spoken_lower in file.lower() or spoken_lower.replace(" ", "_") in file.lower():
                found_files.append(os.path.join(root, file))

    # Remove duplicates
    found_files = list(set(found_files))

    # ==========================================
    # 🧠 THE SELECTION MENU
    # ==========================================
    if len(found_files) == 0:
        print(f"❌ Could not find '{spoken_name}' anywhere on the system.")
        return None
        
    elif len(found_files) == 1:
        print(f"✅ Found exactly one match: {found_files[0]}")
        return found_files[0]
        
    else:
        print(f"\n⚠️ Deep Scan found {len(found_files)} files matching '{spoken_name}':")
        for index, path in enumerate(found_files):
            print(f"  [{index + 1}] {path}")
            
        while True:
            choice = input("\n👉 Enter the file number (or say 'cancel'): ").strip().lower()
            
            if choice in ['0', 'cancel', 'stop', 'abort', 'exit', 'nevermind', 'no']:
                print("❌ Attachment cancelled.")
                return None
                
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(found_files):
                    print(f"✅ Selected: {found_files[idx]}")
                    return found_files[idx]
                else:
                    print("❌ Invalid number. Please pick a number from the list.")
            except ValueError:
                print("❌ Please enter a valid number or say 'cancel'.")