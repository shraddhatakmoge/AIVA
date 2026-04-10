import re
import os

def process_nlp(command, current_app="notepad"):
    raw_text_command = command.strip() 
    cmd = command.lower().strip()

    # --- Brain Polish (Filler removal) ---
    fillers = ["please", "jarvis", "can you", "could you", "i want to", "just", "kindly", "hey"]
    for word in fillers:
        cmd = re.sub(rf'\b{word}\b', '', cmd)
        raw_text_command = re.sub(rf'\b{word}\b', '', raw_text_command, flags=re.IGNORECASE)

    cmd = re.sub(' +', ' ', cmd).strip()
    raw_text_command = re.sub(' +', ' ', raw_text_command).strip()

    result = {
        "app": None,
        "action": None,
        "text": None,
        "line": None,
        "direction": None,
        "contact": None,
        "folder": None,
        "level": None,
        "style": None,
        "align": None
    }

    # =========================================
    # 🧠 STEP 1: EXPLICIT APP DETECTION
    # =========================================
    if "spotify" in cmd or "music" in cmd or "song" in cmd:
        result["app"] = "spotify"
    elif any(x in cmd for x in ["file", "folder", "search for", "find", "document"]):
        result["app"] = "file_system"
    elif any(x in cmd for x in ["powerpoint", "presentation","ppt", "slide", "title", "content"]):
        result["app"] = "powerpoint"
    elif ("word" in cmd and not any(x in cmd for x in ["delete word", "replace word", "style word", "make word", "make the word"])) or "ms word" in cmd:
        result["app"] = "word"
    elif "calculator" in cmd or "calculate" in cmd or "+" in cmd or "-" in cmd or "*" in cmd or "/" in cmd:
        result["app"] = "calculator"
    elif "whatsapp" in cmd or "message" in cmd or "call" in cmd:
        result["app"] = "whatsapp"
    elif "notepad" in cmd:
         result["app"] = "notepad"
    else:
        # 🔥 THE MAGIC TRICK: If they didn't specify an app, use the Memory!
        result["app"] = current_app
    

    # =========================================
    # 📂 STEP 2: FILE SYSTEM (PRIORITY OVERRIDE)
    # =========================================
    # 🔥 THIS MUST BE HERE, BEFORE POWERPOINT OR NOTEPAD LOGIC
    if result["app"] == "file_system":
        
        if "create folder" in cmd or "make folder" in cmd: 
            return {"app": "file_system", "intent": "create_folder", "entities": {"path": cmd.replace("create folder", "").replace("make folder", "").strip()}}
        
        elif "create file" in cmd or "make file" in cmd: 
            return {"app": "file_system", "intent": "create_file", "entities": {"path": cmd.replace("create file", "").replace("make file", "").strip()}}
        
        elif "delete folder" in cmd:
            return {"app": "file_system", "intent": "delete_folder", "entities": {"path": cmd.replace("delete folder", "").strip()}}
            
        elif "delete file" in cmd or "delete" in cmd:
            return {"app": "file_system", "intent": "delete_file", "entities": {"path": cmd.replace("delete file", "").replace("delete", "").strip()}}

        elif "search for" in cmd or "find file" in cmd: 
            return {"app": "file_system", "intent": "search_file", "entities": {"filename": cmd.replace("search for", "").replace("find file", "").strip(), "directory": os.path.expanduser("~")}}

        elif "move" in cmd and "to" in cmd:
            parts = cmd.replace("move file", "").replace("move folder", "").replace("move", "").split(" to ")
            if len(parts) == 2:
                return {"app": "file_system", "intent": "move_file", "entities": {"source": parts[0].strip(), "destination": parts[1].strip()}}
                
        elif "copy" in cmd and "to" in cmd:
            parts = cmd.replace("copy file", "").replace("copy folder", "").replace("copy", "").split(" to ")
            if len(parts) == 2:
                return {"app": "file_system", "intent": "copy_file", "entities": {"source": parts[0].strip(), "destination": parts[1].strip()}}

        elif "rename" in cmd and "to" in cmd:
            parts = cmd.replace("rename file", "").replace("rename folder", "").replace("rename", "").split(" to ")
            if len(parts) == 2:
                return {"app": "file_system", "intent": "rename_file", "entities": {"old_path": parts[0].strip(), "new_path": parts[1].strip()}}

        # Add this right after your "create" and "delete" checks!
        elif "open folder" in cmd or "open file" in cmd:
            target = cmd.replace("open folder", "").replace("open file", "").replace("open", "").strip()
            return {"app": "file_system", "intent": "open_item", "entities": {"path": target}}

    # =========================================
    # 📊 POWERPOINT LOGIC
    # =========================================
    powerpoint_keywords = ["powerpoint", "presentation", "slide", "title", "content", "subtitle", "show", "slideshow", "present", "theme", "design"]
    
    # 🔥 THE FIX: Only enter this block if it's explicitly PowerPoint
    # We removed "next" and "previous" from the keywords list above to prevent stealing
    if result["app"] == "powerpoint" or any(x in cmd for x in powerpoint_keywords):
        result["app"] = "powerpoint"
        
        if "open" in cmd: result["action"] = "open"
        elif "close" in cmd: result["action"] = "close"
        elif "add slide" in cmd or "new slide" in cmd: result["action"] = "add_slide"
        elif "title" in cmd:
            result["action"] = "set_title"
            result["text"] = re.sub(r'(?i).*title\s+(?:to\s+)?', '', raw_text_command).strip()
        elif "content" in cmd:
            result["action"] = "set_content"
            result["text"] = re.sub(r'(?i).*content\s+(?:to\s+)?', '', raw_text_command).strip()
        elif "delete" in cmd or "remove" in cmd:
            result["action"] = "delete_slide"
            match = re.search(r"slide\s+(\d+)", cmd)
            result["text"] = match.group(1) if match else None
        elif any(x in cmd for x in ["slideshow", "present", "start show"]):
            result["action"] = "start_slideshow"
        elif any(x in cmd for x in ["next", "forward", "after"]):
            result["action"] = "navigate"
            result["text"] = "next"
            return result
        elif any(x in cmd for x in ["previous", "back", "before"]):
            result["action"] = "navigate"
            result["text"] = "previous"
            return result
        elif any(x in cmd for x in ["stop", "exit", "end"]) and "slideshow" in cmd:
            result["action"] = "stop_slideshow"
            return result
        elif any(x in cmd for x in ["go to", "show"]):
            result["action"] = "navigate"
            match = re.search(r"slide\s+(\d+)", cmd)
            result["text"] = match.group(1) if match else None
        elif "theme" in cmd or "design" in cmd:
            result["action"] = "apply_theme"
            theme = re.sub(r'(?i).*theme\s+|.*design\s+', '', raw_text_command).strip()
            result["text"] = theme if theme else "Office Theme"
        return result
            
    # =========================================
    # 📄 MS WORD LOGIC 
    # =========================================
    if result["app"] == "word":
        if "open file" in cmd or "open document" in cmd:
            result["action"] = "open_file"
            for loc in ["desktop", "documents", "downloads"]:
                if loc in cmd: result["folder"] = loc
            clean_cmd = re.sub(r'open (file|document)|in word|from \w+|on \w+', '', cmd).strip()
            result["text"] = clean_cmd
        elif "open" in cmd and "file" not in cmd: result["action"] = "open"
        elif "close" in cmd: result["action"] = "close"
        elif "new document" in cmd or "new file" in cmd: result["action"] = "new"
        elif "write" in cmd or "type" in cmd:
            parts = re.split(r'(?i)\b(?:write|type|add)\b\s+', raw_text_command)
            text_to_write = parts[-1].strip() if len(parts) > 1 else ""
            return {"app": "word", "action": "write", "text": text_to_write}
        elif "save" in cmd:
            result["action"] = "save"
            
            # 🔥 IMPROVED REGEX: Specifically looks for the name after "as" or "named"
            # It captures everything until it hits "on", "in", or the end of the string.
            name_match = re.search(r"(?:as|named|called|name)\s+([\w\d_-]+)", cmd)
            
            if name_match:
                filename = name_match.group(1).strip()
                result["text"] = f"{filename}.docx"
            else:
                # Only use "Document.docx" if absolutely no name was found
                result["text"] = "Document.docx"

            # 📂 PORTABLE FOLDER DETECTION
            if "desktop" in cmd:
                result["folder"] = os.path.expanduser("~\\Desktop")
            elif "documents" in cmd:
                result["folder"] = os.path.expanduser("~\\Documents")
            else:
                result["folder"] = os.path.expanduser("~\\Desktop") # Default
                
            return result
        elif "heading" in cmd:
            result["action"] = "heading"
            match = re.search(r"heading (\d)", cmd)
            result["level"] = int(match.group(1)) if match else 1
        elif "make" in cmd and ("word" in cmd or "text" in cmd):
            result["action"] = "style_specific"
            target_match = re.search(r"(?:word|text)\s+([\w'-]+)", cmd)
            if target_match: result["text"] = target_match.group(1).strip()
            colors = ["red", "blue", "green", "yellow", "black", "purple", "orange"]
            for c in colors:
                if c in cmd: result["color"] = c; break
            size_match = re.search(r"size\s+(\d+)", cmd)
            if size_match: result["size"] = int(size_match.group(1))
            if "bold" in cmd: result["style"] = "bold"
            if "italic" in cmd: result["style"] = "italic"
            if "underline" in cmd: result["style"] = "underline"
        # Update these checks in the Word section of nlp.py
        elif any(x in cmd for x in ["bold", "italic", "underline"]):
            for s in ["bold", "italic", "underline"]:
                if s in cmd: result["style"] = s; break
            
            result["action"] = "style_specific"
            # 🔥 THE MULTI-WORD FIX: 
            # Captures everything after "the words" or "the word"
            match = re.search(r"(?:bold|italic|underline)(?: the word[s]?) (.*)", cmd)
            if match:
                # Store as a list if separated by 'and' or commas
                raw_words = match.group(1).replace(" and ", ",").split(",")
                result["text"] = [w.strip() for w in raw_words if w.strip()]
            return result
        
        # Add these alongside your 'bold' check in nlp.py
        elif "italic" in cmd or "italicize" in cmd:
            result["action"] = "style_specific"
            result["style"] = "italic"
            match = re.search(r"(?:italicize|italic)(?: the word)? (.*)", cmd)
            if match: result["text"] = match.group(1).strip()
            return result

        elif "underline" in cmd:
            result["action"] = "style_specific"
            result["style"] = "underline"
            match = re.search(r"underline(?: the word)? (.*)", cmd)
            if match: result["text"] = match.group(1).strip()
            return result
        elif "bold" in cmd:
            result["action"] = "style_specific"
            result["style"] = "bold"
            # Extract the word to be bolded (e.g., "bold the word test" -> "test")
            match = re.search(r"(?:bold|make bold)(?: the word)? (.*)", cmd)
            if match:
                result["text"] = match.group(1).strip()
            return result
        elif "replace" in cmd or "change" in cmd:
            match = re.search(r"(?:replace|change) (.*?) (?:with|to) (.*)", cmd)
            if match:
                result["action"] = "replace"
                result["old_text"] = match.group(1).strip()
                result["new_text"] = match.group(2).strip()
        elif "delete word" in cmd:
            result["action"] = "delete"
            result["text"] = cmd.split("delete word")[-1].strip()
        elif "insert" in cmd or "add" in cmd:
            match = re.search(r"(?:insert|add) (.*?) (?:at|on|in) line (\d+)", cmd)
            if match:
                result["action"] = "insert"; result["text"] = match.group(1).strip(); result["line"] = int(match.group(2))
            else:
                result["action"] = "insert"; result["text"] = cmd.replace("insert", "").replace("add", "").strip()
        elif "align" in cmd or "center" in cmd:
            result["action"] = "alignment"
            if "center" in cmd: result["align"] = "center"
            elif "right" in cmd: result["align"] = "right"
            elif "left" in cmd: result["align"] = "left"
            elif "justify" in cmd: result["align"] = "justify"
            return result
        
        elif "clear" in cmd or "empty" in cmd: result["action"] = "clear"
        elif "read" in cmd: result["action"] = "read"
        elif "undo" in cmd: result["action"] = "style"; result["style"] = "undo"
        elif "new line" in cmd: result["action"] = "new_line"
        elif "paragraph" in cmd: result["action"] = "new_paragraph"
        elif "move" in cmd:
            for d in ["left", "right", "up", "down"]:
                if d in cmd: result["action"] = "move"; result["direction"] = d; break
        return result

    # =========================================
    # 📝 CLEANED NOTEPAD LOGIC
    # =========================================
    # Since Notepad is our default, we handle its commands directly here
    
    # 1. OPEN / CLOSE
    if "open notepad" in cmd: return {"app": "notepad", "action": "open"}
    elif "close notepad" in cmd: return {"app": "notepad", "action": "close"}

    # 2. BULLETPROOF WRITE LOGIC
    if "write" in cmd or "type" in cmd or "say " in cmd:
        # Splits the string perfectly at the trigger word, keeping everything after it
        parts = re.split(r'(?i)\b(?:write|type|add|say)\b\s+', raw_text_command)
        text_to_write = parts[-1].strip() if len(parts) > 1 else ""
        return {"app": result["app"] or "notepad", "action": "write", "text": text_to_write}

    # 3. SMART SAVE 
    match_save = re.search(r"save (?:it |file )?(?:as|called|with name)? (.*)", raw_text_command, re.IGNORECASE)
    if match_save:
        filename = match_save.group(1).strip().replace(".", "").replace(",", "")
        if not filename.endswith(".txt"): filename += ".txt"
        return {"app": result["app"] or "notepad", "action": "save", "text": filename}
    elif "save" in cmd:
        return {"app": result["app"] or "notepad", "action": "save", "text": "test.txt"}

    # 4. DELETE / EDIT
    match_del_line = re.search(r"delete word (.*?) from line (\d+)", cmd)
    if match_del_line:
        return {"app": result["app"] or "notepad", "action": "delete", "text": match_del_line.group(1).strip(), "line": int(match_del_line.group(2))}
    # Extracts the number so JARVIS knows WHICH line to delete
    match_del_line_num = re.search(r"delete line (\d+)", cmd)
    if match_del_line_num:
        return {"app": result["app"] or "notepad", "action": "delete_line", "line": int(match_del_line_num.group(1))}
    elif "delete" in cmd:
        target = cmd.replace("delete", "").replace("word", "").strip()
        return {"app": result["app"] or "notepad", "action": "delete", "text": target}
    
    match_replace = re.search(r"(?:replace|change|swap|turn) (.*?) (?:with|to|for|into) (.*)", cmd)
    if match_replace:
        return {"app": result["app"] or "notepad", "action": "replace", "old_text": match_replace.group(1).strip(), "new_text": match_replace.group(2).strip()}

    # 5. INSERT
    match_ins_line = re.search(r"(?:insert|add|put|squeeze) (.*?) (?:at|on|in|into) line (\d+)", cmd)
    if match_ins_line:
        return {"app": result["app"] or "notepad", "action": "insert", "text": match_ins_line.group(1).strip(), "line": int(match_ins_line.group(2))}
    elif "insert" in cmd or "add" in cmd:
        text = cmd.replace("insert", "").replace("add", "").strip()
        return {"app": result["app"] or "notepad", "action": "insert", "text": text}

    # 6. FORMATTING / MOVEMENT
    if "undo" in cmd: return {"app": result["app"] or "notepad", "action": "undo"}
    elif "redo" in cmd: return {"app": result["app"] or "notepad", "action": "redo"}
    elif "new paragraph" in cmd: return {"app": result["app"] or "notepad", "action": "new_paragraph"}
    elif "new line" in cmd: return {"app": result["app"] or "notepad", "action": "new_line"}
    elif "space" in cmd: return {"app": result["app"] or "notepad", "action": "space"}
    elif "move" in cmd:
        for direction in ["left", "right", "up", "down"]:
            if direction in cmd: return {"app": result["app"] or "notepad", "action": "move", "direction": direction}

    # 7. UTILITY
    if "clear" in cmd or "empty" in cmd: return {"app": result["app"] or "notepad", "action": "clear"}
    elif "new file" in cmd or "create file" in cmd: return {"app": result["app"] or "notepad", "action": "new"}
    elif "read" in cmd: return {"app": result["app"] or "notepad", "action": "read"}
    
    # =========================================
    # 💬 SPOTIFY
    # =========================================
    if result["app"] == "spotify":
        # Explicitly catch 'open' so it never goes to the LLM
        
        # 🔥 THE MOOD MAPPING
        mood_map = {
            "sad": ["sad", "low", "depressed", "heartbreak"],
            "party": ["party", "dance", "club", "vibes"],
            "chill": ["chill", "relax", "study", "lofi", "flow"],
            "romantic": ["love", "romantic", "date"],
            "energy": ["gym", "workout", "energy", "power"]
        }
        
        query_map = {
            "sad": "Sad Songs for Soul",
            "party": "Top Party Hits 2026",
            "chill": "Lofi Hip Hop Radio - Beats to Relax/Study to",
            "romantic": "Romantic Evening Playlist",
            "energy": "High Energy Workout Mix"
        }

        # Check for mood keywords
        for mood, keywords in mood_map.items():
            if any(word in cmd for word in keywords):
                print(f"🎵 JARVIS: Selecting a {mood} playlist for your current vibe.")
                return {"app": "spotify", "action": "play", "text": query_map[mood]}
        
        # Fallback for "play something as per your mood"
        if "your mood" in cmd or "you like" in cmd:
            print("🤖 JARVIS: Choosing my 'Digital Flow' mix for us.")
            return {"app": "spotify", "action": "play", "text": "Sture Zetterberg Mix"}
        
        if "open" in cmd:
            return {"app": "spotify", "action": "open"}
        
        # Explicitly catch 'close'
        if "close" in cmd:
            return {"app": "spotify", "action": "close"}
   
    if "like" in cmd:
        return {"app": "spotify", "action": "like"} # Matches execute_action key
    
    mood_map = {"sad": ["sad", "low", "cry", "depressed"], "party": ["party", "dance", "fun"], "chill": ["chill", "relax", "calm"], "romantic": ["love", "romantic"], "energy": ["gym", "workout", "energy"]}
    query_map = {"sad": "sad songs playlist", "party": "party songs playlist", "chill": "chill music", "romantic": "romantic songs", "energy": "workout music"}
    for mood, words in mood_map.items():
        if any(word in cmd for word in words): return {"app": "spotify", "action": "play", "text": query_map[mood]}

    if "play" in cmd or "listen" in cmd:
        text = cmd
        for word in ["play", "listen", "to", "song", "music", "please", "can you", "i want", "me"]: text = text.replace(word, "")
        if text.strip(): return {"app": "spotify", "action": "play", "text": text.strip()}

    if "pause" in cmd: return {"app": "spotify", "action": "pause"}
    if "resume" in cmd or "play" == cmd: return {"app": "spotify", "action": "resume"}
    if "next" in cmd: return {"app": "spotify", "action": "next"}
    if "previous" in cmd: return {"app": "spotify", "action": "previous"}
    if "mute" in cmd: return {"app": "spotify", "action": "mute"}
    if "volume up" in cmd: return {"app": "spotify", "action": "volume_up"}
    if "volume down" in cmd: return {"app": "spotify", "action": "volume_down"}
        
    # =========================================
    # 🧮 CALCULATOR 
    # =========================================
    if "open calculator" in cmd: return {"app": "calculator", "action": "open"}
    if "close calculator" in cmd: return {"app": "calculator", "action": "close"}
    
    if re.search(r"\b(square|root|factorial|pi|power)\b", cmd): return {"app": "calculator", "action": "calculate", "expression": None}
    
    if any(word in cmd for word in ["calculate", "what is", "+", "-", "*", "/", "divide", "multiply"]):
        expr = cmd.replace("plus", "+").replace("minus", "-").replace("multiply", "*").replace("multiplied by", "*").replace("x", "*").replace("divide", "/").replace("divided by", "/")
        expr = re.sub(r"[a-zA-Z]", "", expr).strip()
        return {"app": "calculator", "action": "calculate", "expression": expr}
    
    # =========================================
    # 💬 WHATSAPP
    # =========================================
    if "open whatsapp" in cmd: return {"app": "whatsapp", "action": "open"}
    elif "close whatsapp" in cmd: return {"app": "whatsapp", "action": "close"}
    elif "voice message" in cmd or "voice note" in cmd:
        match = re.search(r"voice (?:message|note)(?: to)? (.+)", cmd)
        return {"app": "whatsapp", "action": "voice_note", "contact": match.group(1).strip() if match else None}   
    elif "stop recording" in cmd or "stop voice" in cmd: return {"app": "whatsapp", "action": "stop_voice"}
    elif "message to" in cmd or "whatsapp to" in cmd:
        match = re.search(r"to (.*?)(?: saying| that says|:|,| ) (.*)", cmd)
        if match: return {"app": "whatsapp", "action": "send_to", "contact": match.group(1).strip(), "text": match.group(2).strip()}
        else: return {"app": "whatsapp", "action": "send_to", "contact": cmd.split("to")[-1].strip(), "text": ""}
    elif "send message" in cmd: return {"app": "whatsapp", "action": "send", "text": cmd.split("message", 1)[-1].strip()}
    elif "send screenshot to" in cmd: return {"app": "whatsapp", "action": "screenshot", "contact": cmd.split("to")[-1].strip()}
    elif "video call" in cmd: return {"app": "whatsapp", "action": "video_call", "contact": cmd.replace("video call", "").strip()}
    elif "voice call" in cmd or "call" in cmd: return {"app": "whatsapp", "action": "voice_call", "contact": cmd.replace("voice call", "").replace("call", "").strip()}
    if "mute" in command and "call" in command: return {"app": "system", "action": "mute_mic"}
    if "unmute" in command: return {"app": "system", "action": "unmute_mic"}
    elif "read my last message" in cmd: return {"app": "whatsapp", "action": "read_my"}
    if "end call" in command or "cut call" in command: return {"app": "whatsapp", "action": "end_call"}
    if "status" in command: return {"app": "whatsapp", "action": "open_status", "contact": command.split()[-1]}
    if "read" in cmd and "message" in cmd:
        words = cmd.split()
        contact = words[words.index("from") + 1] if "from" in words and words.index("from") + 1 < len(words) else None
        return {"app": "whatsapp", "action": "read", "contact": contact, "count": 3}
    elif "send contact" in cmd and "to" in cmd:
        try:
            contact_to_share, target_person = cmd.split("send contact ")[1].split(" to ")
            return {"app": "whatsapp", "action": "send_contact_card", "target": target_person.strip(), "share_name": contact_to_share.strip()}
        except: pass
    elif "send" in cmd and "to" in cmd:
        try:
            location = "desktop" if "from desktop" in cmd else "downloads" if "from downloads" in cmd else "documents" if "from documents" in cmd else None
            cmd_clean = cmd.replace("from desktop", "").replace("from downloads", "").replace("from documents", "").strip()
            spoken_file, contact = cmd_clean.split("send ")[1].split(" to ")
            clean_file = spoken_file.replace("file ", "").replace("attachment ", "").replace("document ", "").strip()
            return {"app": "whatsapp", "action": "send_attachment", "contact": contact.strip(), "file_name": clean_file, "location": location}
        except: pass
    elif "read last message sent by" in cmd: return {"app": "whatsapp", "action": "read_from_contact", "contact": cmd.split("by")[-1].strip()}

  
    # =========================================
    # 📂 STEP 2: FILE SYSTEM (PRIORITY OVERRIDE)
    # =========================================
    # 🔥 PLACE THIS BEFORE ANY OTHER ACTION CHECKS!
    if result["app"] == "file_system":
        
        if "create folder" in cmd or "make folder" in cmd: 
            return {"app": "file_system", "intent": "create_folder", "entities": {"path": cmd.replace("create folder", "").replace("make folder", "").strip()}}
        
        elif "create file" in cmd or "make file" in cmd: 
            return {"app": "file_system", "intent": "create_file", "entities": {"path": cmd.replace("create file", "").replace("make file", "").strip()}}
        
        elif "delete folder" in cmd:
            return {"app": "file_system", "intent": "delete_folder", "entities": {"path": cmd.replace("delete folder", "").strip()}}
            
        elif "delete file" in cmd or "delete" in cmd:
            return {"app": "file_system", "intent": "delete_file", "entities": {"path": cmd.replace("delete file", "").replace("delete", "").strip()}}

        elif "search for" in cmd or "find file" in cmd: 
            return {"app": "file_system", "intent": "search_file", "entities": {"filename": cmd.replace("search for", "").replace("find file", "").strip(), "directory": os.path.expanduser("~")}}

        elif "move" in cmd and "to" in cmd:
            parts = cmd.replace("move file", "").replace("move folder", "").replace("move", "").split(" to ")
            if len(parts) == 2:
                return {"app": "file_system", "intent": "move_file", "entities": {"source": parts[0].strip(), "destination": parts[1].strip()}}
                
        elif "copy" in cmd and "to" in cmd:
            parts = cmd.replace("copy file", "").replace("copy folder", "").replace("copy", "").split(" to ")
            if len(parts) == 2:
                return {"app": "file_system", "intent": "copy_file", "entities": {"source": parts[0].strip(), "destination": parts[1].strip()}}

        elif "rename" in cmd and "to" in cmd:
            parts = cmd.replace("rename file", "").replace("rename folder", "").replace("rename", "").split(" to ")
            if len(parts) == 2:
                return {"app": "file_system", "intent": "rename_file", "entities": {"old_path": parts[0].strip(), "new_path": parts[1].strip()}}
    return result