import re

def process_nlp(command):
    cmd = command.lower()

    # 🔥 BRAIN POLISH: Remove conversational filler words
    fillers = ["please", "jarvis", "can you", "could you", "i want to", "just", "kindly", "hey", "send a"]
    for word in fillers:
        cmd = cmd.replace(word, "")
    
    # Clean up any weird double spaces we accidentally created
    cmd = re.sub(' +', ' ', cmd).strip()

    result = {
        "app": None,
        "action": None,
        "text": None,
        "line": None,
        "direction": None,
        "contact": None
    }
    
     # =========================================
    # 💬 SPOTIFY
    # =========================================
    
    cmd = cmd.lower().strip()

    # ❤️ LIKE SONG
    if "like song" in cmd or "add to favorites" in cmd:
        return {
            "app": "spotify",
            "action": "like"
        }


    # 🎧 MOOD DETECTION (SMART)
    mood_map = {
        "sad": ["sad", "low", "cry", "depressed"],
        "party": ["party", "dance", "fun"],
        "chill": ["chill", "relax", "calm"],
        "romantic": ["love", "romantic"],
        "energy": ["gym", "workout", "energy"]
    }

    query_map = {
        "sad": "sad songs playlist",
        "party": "party songs playlist",
        "chill": "chill music",
        "romantic": "romantic songs",
        "energy": "workout music"
    }

    for mood, words in mood_map.items():
        if any(word in cmd for word in words):
            return {
                "app": "spotify",
                "action": "play",
                "text": query_map[mood]
            }


    # 🎧 SMART PLAY (IMPORTANT)
    if "play" in cmd or "listen" in cmd:

        text = cmd

        remove_words = [
            "play", "listen", "to", "song", "music",
            "please", "can you", "i want", "me"
        ]

        for word in remove_words:
            text = text.replace(word, "")

        text = text.strip()

        if text:
            return {
                "app": "spotify",
                "action": "play",
                "text": text
            }


    # 🎧 CONTROLS
    if "pause" in cmd:
        return {"app": "spotify", "action": "pause"}

    if "resume" in cmd or "play" == cmd:
        return {"app": "spotify", "action": "resume"}

    if "next" in cmd:
        return {"app": "spotify", "action": "next"}

    if "previous" in cmd:
        return {"app": "spotify", "action": "previous"}

    if "mute" in cmd:
        return {"app": "spotify", "action": "mute"}

    if "volume up" in cmd:
        return {"app": "spotify", "action": "volume_up"}

    if "volume down" in cmd:
        return {"app": "spotify", "action": "volume_down"}
        
    # =========================================
    # 🧮 CALCULATOR 
    # =========================================
    if "open calculator" in cmd:
        return {"app": "calculator", "action": "open"}

    if "close calculator" in cmd:
        return {"app": "calculator", "action": "close"}

    # 🔥 ADVANCED MATH COMMANDS (MUST BE ABOVE BASIC MATH)
    if any(word in cmd for word in ["square", "root", "factorial", "pi", "power"]):
        return {
            "app": "calculator",
            "action": "calculate",
            "expression": None   # Force calculator.py to handle the advanced logic
        }   

    # ➕ BASIC MATH COMMANDS
    if any(word in cmd for word in ["calculate", "what is", "+", "-", "*", "/", "divide", "multiply"]):
        expr = cmd
        # replace words with symbols
        expr = expr.replace("plus", "+")
        expr = expr.replace("minus", "-")
        expr = expr.replace("multiply", "*")
        expr = expr.replace("multiplied by", "*")
        expr = expr.replace("x", "*")
        expr = expr.replace("divide", "/")
        expr = expr.replace("divided by", "/")

        # remove text
        expr = re.sub(r"[a-zA-Z]", "", expr).strip()

        return {
            "app": "calculator",
            "action": "calculate",
            "expression": expr
        }
    
    # =========================================
    # 💬 WHATSAPP (TOP PRIORITY)
    # =========================================

    # OPEN / CLOSE
    if "open whatsapp" in cmd:
        return {"app": "whatsapp", "action": "open"}

    elif "close whatsapp" in cmd:
        return {"app": "whatsapp", "action": "close"}

    # 💬 SEND MESSAGE TO CONTACT (SMARTER REGEX)
    elif "message to" in cmd or "whatsapp to" in cmd:
        try:
            # Matches: "message to [Contact] saying [Text]" OR "message to [Contact] [Text]"
            match = re.search(r"to (.*?)(?: saying| that says|:|,| ) (.*)", cmd)
            
            if match:
                contact = match.group(1).strip()
                text = match.group(2).strip()
            else:
                # Fallback if you just say "message to mummy"
                contact = cmd.split("to")[-1].strip()
                text = ""

            return {
                "app": "whatsapp",
                "action": "send_to",
                "contact": contact,
                "text": text
            }
        except:
            pass

    # SEND NORMAL MESSAGE
    elif "send message" in cmd:
        return {
            "app": "whatsapp",
            "action": "send",
            "text": cmd.split("message", 1)[-1].strip()
        }

    # 📸 SCREENSHOT
    elif "send screenshot to" in cmd:
        contact = cmd.split("to")[-1].strip()
        return {
            "app": "whatsapp",
            "action": "screenshot",
            "contact": contact
        }

    # VIDEO CALL
    elif "video call" in cmd:
        contact = cmd.replace("video call", "").strip()
        return {"app": "whatsapp", "action": "video_call", "contact": contact}

    # VOICE CALL
    elif "voice call" in cmd or "call" in cmd:
        contact = cmd.replace("voice call", "").replace("call", "").strip()
        return {"app": "whatsapp", "action": "voice_call", "contact": contact}
            
    # MUTE/ UNMUTE
    if "mute" in command and "call" in command:
        return {"app": "system", "action": "mute_mic"}

    if "unmute" in command:
        return {"app": "system", "action": "unmute_mic"}

    # 🔊 READ MY MESSAGE
    elif "read my last message" in cmd:
        return {
            "app": "whatsapp",
            "action": "read_my"
        }
    
    if "end call" in command or "cut call" in command:
        return {"app": "whatsapp", "action": "end_call"}
    
    # CHECK STATUS
    if "status" in command:
        words = command.split()

        # get last word as contact
        contact = words[-1]

        return {
            "app": "whatsapp",
            "action": "open_status",
            "contact": contact
        }

    # 💬 WHATSAPP VOICE MESSAGE
    if "voice message" in cmd or "voice note" in cmd:
        result["app"] = "whatsapp"
        result["action"] = "voice_note"

        words = cmd.split()

        if "to" in words:
            idx = words.index("to")
            if idx + 1 < len(words):
                result["contact"] = words[idx + 1]
        else:
            result["contact"] = words[-1]

        return result
        
    # 📩 READ WHATSAPP MESSAGES
    if "read" in cmd and "message" in cmd:
        result["app"] = "whatsapp"
        result["action"] = "read"

        # extract contact name
        words = cmd.split()
        if "from" in words:
            idx = words.index("from")
            if idx + 1 < len(words):
                result["contact"] = words[idx + 1]

        # optional: number of messages
        result["count"] = 3

        return result
    
    # 👤 SEND CONTACT CARD (SPECIFIC - Put this first!)
    elif "send contact" in cmd and "to" in cmd:
        try:
            after_cmd = cmd.split("send contact ")[1]
            contact_to_share, target_person = after_cmd.split(" to ")
            
            return {
                "app": "whatsapp",
                "action": "send_contact_card",
                "target": target_person.strip(),
                "share_name": contact_to_share.strip()
            }
        except:
            pass
    
    # 📎 SEND SMART ATTACHMENT (WITH LOCATION CAPABILITY)
    elif "send" in cmd and "to" in cmd:
        try:
            # 1. Check for specific locations and remove them from the command
            location = None
            if "from desktop" in cmd:
                location = "desktop"
                cmd = cmd.replace("from desktop", "").strip()
            elif "from downloads" in cmd:
                location = "downloads"
                cmd = cmd.replace("from downloads", "").strip()
            elif "from documents" in cmd:
                location = "documents"
                cmd = cmd.replace("from documents", "").strip()

            # 2. Extract file and contact (Example: "send html file to mummy")
            after_send = cmd.split("send ")[1]
            spoken_file, contact = after_send.split(" to ")
            
            clean_file = spoken_file.replace("file ", "").replace("attachment ", "").replace("document ", "").strip()
            
            return {
                "app": "whatsapp",
                "action": "send_attachment",
                "contact": contact.strip(),
                "file_name": clean_file,
                "location": location  # 🔥 Pass the location to main!
            }
        except:
            pass
       
        
    # (OPTIONAL KEEP)
    elif "read last message sent by" in cmd:
        name = cmd.split("by")[-1].strip()
        return {
            "app": "whatsapp",
            "action": "read_from_contact",
            "contact": name
        }

    # =========================================
    # 📝 NOTEPAD SECTION
    # =========================================
    
    if "open" in cmd:
        result["action"] = "open"

    elif "close" in cmd:
        result["action"] = "close"
        
    # 🆕 NEW FILE / CREATE
    if any(word in cmd for word in ["new file", "create file", "clear notepad"]):
        return {
            "app": "notepad",
            "action": "new"
        }

    # ✍️ WRITE / TYPE 
    elif "write" in cmd or "type" in cmd:
        # Matches "write [text]" or "type [text]" 
        match = re.search(r"(?:write|type) (.*)", cmd)
        return {
            "app": "notepad",
            "action": "write",
            "text": match.group(1).strip() if match else None
        }

    # 📖 READ COMMAND
    elif "read" in cmd:
        return {
            "app": "notepad",
            "action": "read"
        }
    
    # 🔄 REPLACE WORD
    elif "replace" in cmd and "with" in cmd:
        # Matches "replace old_word with new_word"
        match = re.search(r"replace (.*?) with (.*)", cmd)
        if match:
            return {
                "app": "notepad",
                "action": "replace",
                "old_text": match.group(1).strip(),
                "new_text": match.group(2).strip()
            }
            
    # 💾 SAVE FILE
    elif "save" in cmd:
        # Strategy A: Look for "save as [filename]"
        match = re.search(r"save.*? as (.*)", cmd)
        
        if match:
            filename = match.group(1).strip()
            # Automatically add .txt if you forgot to say it
            if not filename.endswith(".txt"):
                filename += ".txt"
            return {"app": "notepad", "action": "save", "text": filename}
        
        # Strategy B: If you just say "save my-file", take the last word
        else:
            words = cmd.split()
            filename = words[-1] + ".txt" if ".txt" not in words[-1] else words[-1]
            return {"app": "notepad", "action": "save", "text": filename}

    # ➕ INSERT / ADD text at cursor
    elif "insert" in cmd or "add" in cmd:
        match = re.search(r"(?:insert|add) (.*)", cmd)
        return {
            "app": "notepad",
            "action": "insert",
            "text": match.group(1).strip() if match else None
        }

    # 🗑️ DELETE WORD
    elif "delete" in cmd or "remove" in cmd:
        match = re.search(r"(?:delete|remove) word (.*)", cmd)
        return {
            "app": "notepad",
            "action": "delete",
            "text": match.group(1).strip() if match else None
        }

    # 🧭 NAVIGATION & FORMATTING
    elif "move" in cmd:
        for direction in ["left", "right", "up", "down"]:
            if direction in cmd:
                return {"app": "notepad", "action": "move", "direction": direction}

    elif "paragraph" in cmd:
        return {"app": "notepad", "action": "new_paragraph"}

    elif "new line" in cmd:
        return {"app": "notepad", "action": "new_line"}
    
    # =========================================
    # 🧠 SMART APP DETECTION
    # =========================================
    # Automatically tag the app if you mention it!
    target_apps = ["notepad", "word", "spotify", "vscode", "powerpoint", "calculator", "whatsapp"]
    for a in target_apps:
        if a in cmd:
            result["app"] = a
            # Remove the app name from the command so it doesn't get caught as text!
            cmd = cmd.replace(f"in {a}", "").replace(f"on {a}", "").replace(a, "").strip()



    # DEFAULT APP FALLBACK
    if result["app"] is None:
        result["app"] = "notepad"

    return result