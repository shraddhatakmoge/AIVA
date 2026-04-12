import re
import os

def process_nlp(command, current_app="notepad"):
    raw_text_command = command.strip() 
    cmd = command.lower().strip()

    # =========================================
    # 🧠 STEP 1: SMART FILLER REMOVAL
    # =========================================
    fillers = [
        "please", "jarvis", "can you", "could you", "i want to", "just", 
        "kindly", "hey", "for me", "a new", "an", "the", "go ahead and"
    ]
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
        "align": None,
        "color": None,  
        "size": None   
    }

    # =========================================
    # 🧠 STEP 2: EXPLICIT APP DETECTION
    # =========================================
    if any(x in cmd for x in ["spotify", "music", "song", "playlist"]):
        result["app"] = "spotify"
    elif "notepad" in cmd:
        result["app"] = "notepad"
    elif any(x in cmd for x in ["file", "folder", "directory", "document"]) and not "open file" in cmd and result["app"] != "word":
        result["app"] = "file_system"
    elif any(x in cmd for x in ["powerpoint", "presentation","ppt", "slide", "slideshow"]):
        result["app"] = "powerpoint"
    elif ("word" in cmd or "document" in cmd) and not any(x in cmd for x in ["delete word", "replace word"]):
        result["app"] = "word"
    elif any(x in cmd for x in ["calculator", "calculate", "math", "+", "-", "*", "/"]):
        result["app"] = "calculator"
    elif any(x in cmd for x in ["whatsapp", "message", "call", "chat"]):
        result["app"] = "whatsapp"
    else:
        result["app"] = current_app 


    # =========================================
    # 📂 STEP 3: FILE SYSTEM (FLEXIBLE REGEX)
    # =========================================
    if result["app"] == "file_system":
        
        match_folder = re.search(r"(?:create|make|generate)(?: folder| directory)(?: called| named)? (.*)", cmd)
        if match_folder: return {"app": "file_system", "intent": "create_folder", "entities": {"path": match_folder.group(1).strip()}}
        
        match_file = re.search(r"(?:create|make|generate)(?: file)(?: called| named)? (.*)", cmd)
        if match_file: return {"app": "file_system", "intent": "create_file", "entities": {"path": match_file.group(1).strip() if match_file.group(1) else "Untitled.txt"}}
        elif "create file" in cmd or "make file" in cmd: return {"app": "file_system", "intent": "create_file", "entities": {"path": "Untitled.txt"}}

        match_del_folder = re.search(r"(?:delete|remove|destroy)(?: folder| directory) (.*)", cmd)
        if match_del_folder: return {"app": "file_system", "intent": "delete_folder", "entities": {"path": match_del_folder.group(1).strip()}}
            
        match_del_file = re.search(r"(?:delete|remove|destroy)(?: file)? (.*)", cmd)
        if match_del_file: return {"app": "file_system", "intent": "delete_file", "entities": {"path": match_del_file.group(1).strip()}}

        match_search = re.search(r"(?:search for|find|look for)(?: file)? (.*)", cmd)
        if match_search: return {"app": "file_system", "intent": "search_file", "entities": {"filename": match_search.group(1).strip(), "directory": os.path.expanduser("~")}}

        match_move = re.search(r"(?:move|transfer) (.*) to (.*)", cmd)
        if match_move: return {"app": "file_system", "intent": "move_file", "entities": {"source": match_move.group(1).strip(), "destination": match_move.group(2).strip()}}
                
        match_copy = re.search(r"(?:copy|duplicate) (.*) to (.*)", cmd)
        if match_copy: return {"app": "file_system", "intent": "copy_file", "entities": {"source": match_copy.group(1).strip(), "destination": match_copy.group(2).strip()}}

        match_rename = re.search(r"(?:rename|change name of) (.*) to (.*)", cmd)
        if match_rename: return {"app": "file_system", "intent": "rename_file", "entities": {"old_path": match_rename.group(1).strip(), "new_path": match_rename.group(2).strip()}}

        match_open = re.search(r"(?:open|launch)(?: file| folder)? (.*)", cmd)
        if match_open: return {"app": "file_system", "intent": "open_item", "entities": {"path": match_open.group(1).strip()}}

    # =========================================
    # 📊 POWERPOINT LOGIC
    # =========================================
    powerpoint_keywords = ["powerpoint", "presentation", "slide", "title", "content", "subtitle", "slideshow", "present", "theme", "design"]
    
    if result["app"] == "powerpoint" or any(x in cmd for x in powerpoint_keywords):
        result["app"] = "powerpoint"
        
        if "open" in cmd: result["action"] = "open"
        elif "close" in cmd: result["action"] = "close"
        elif "add slide" in cmd or "new slide" in cmd: result["action"] = "add_slide"
        
        elif "title" in cmd:
            result["action"] = "set_title"
            match = re.search(r"(?:set|change|make)(?: title)(?: to)? (.*)", raw_text_command, re.IGNORECASE)
            result["text"] = match.group(1).strip() if match else re.sub(r'(?i).*title\s+(?:to\s+)?', '', raw_text_command).strip()
            
        elif "content" in cmd:
            result["action"] = "set_content"
            match = re.search(r"(?:set|change|make)(?: content)(?: to)? (.*)", raw_text_command, re.IGNORECASE)
            result["text"] = match.group(1).strip() if match else re.sub(r'(?i).*content\s+(?:to\s+)?', '', raw_text_command).strip()
            
        elif "delete" in cmd or "remove" in cmd:
            result["action"] = "delete_slide"
            match = re.search(r"(?:delete|remove) slide (\d+)", cmd)
            result["text"] = match.group(1) if match else None
            
        # 🔥 THE FIX: Use a fuzzy regex to catch "slideshow", "slide show", or "slidehsow"
        elif any(x in cmd for x in ["slideshow", "slide show", "slideh", "present"]): 
            result["action"] = "start_slideshow"
            return result
        elif any(x in cmd for x in ["next", "forward"]): return {"app": "powerpoint", "action": "navigate", "text": "next"}
        elif any(x in cmd for x in ["previous", "back"]): return {"app": "powerpoint", "action": "navigate", "text": "previous"}
        elif any(x in cmd for x in ["stop", "exit", "end"]) and "slideshow" in cmd: return {"app": "powerpoint", "action": "stop_slideshow"}
        
        elif "go to slide" in cmd or "show slide" in cmd:
            result["action"] = "navigate"
            match = re.search(r"(?:go to|show) slide (\d+)", cmd)
            result["text"] = match.group(1) if match else None
            
        elif "theme" in cmd or "design" in cmd:
            result["action"] = "apply_theme"
            # 🔥 THE FIX: Use a non-capturing group to ignore "theme" or "design" if the user said it
            match = re.search(r"(?:apply|use|set)(?: theme| design)? (.*)", raw_text_command, re.IGNORECASE)
            if match:
                theme_name = match.group(1).strip()
                # Clean up any leftover words like "theme" or "design" from the start of the string
                theme_name = re.sub(r'^(theme|design)\s+', '', theme_name, flags=re.IGNORECASE)
                result["text"] = theme_name
            else:
                result["text"] = "Office Theme"
            return result
            
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
        # ---------- MS WORD: SAVE AS ----------
        # Move this higher up in your Word block!
        if "save" in cmd:
            result["action"] = "save"
            
            # Use regex to grab the filename specifically
            name_match = re.search(r"(?:as|named|called|name)\s+([\w\d_-]+)", cmd)
            
            if name_match:
                filename = name_match.group(1).strip()
                result["text"] = f"{filename}.docx" # Force .docx for Word
            else:
                result["text"] = "Document.docx"

            # Check for folder preferences
            if "documents" in cmd:
                result["folder"] = os.path.expanduser("~\\Documents")
            else:
                result["folder"] = os.path.expanduser("~\\Desktop")
                
            return result
        elif "heading" in cmd:
            result["action"] = "heading"
            match = re.search(r"heading (\d)", cmd)
            result["level"] = int(match.group(1)) if match else 1

        # ---------- SMART TEXT STYLING (Colors, Bold, Sizes) ----------
        color_list = ["red", "blue", "green", "yellow", "black", "purple", "orange", "pink", "white"]
        style_list = ["bold", "italic", "underline"]
        
        if any(x in cmd for x in color_list + style_list + ["size", "color"]):
            result["action"] = "style_specific"
            
            # 1. Color Extraction
            for c in color_list:
                if c in cmd: result["color"] = c; break
                
            # 2. Style Extraction
            for s in style_list:
                if s in cmd: result["style"] = s; break
                
            # 3. Size Extraction (Fixed to catch any number near 'size')
            size_match = re.search(r"size\s*(\d+)", cmd)
            if size_match: 
                result["size"] = int(size_match.group(1))
            
            # 4. Target Word Extraction (Fixed to strip quotes)
            # This looks for the word after 'word' and cleans off any ' or "
            target_match = re.search(r"word\s+['\"]?([\w-]+)['\"]?", cmd)
            if target_match:
                result["text"] = target_match.group(1).strip()
            
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
    # 📝 NOTEPAD LOGIC (FLEXIBLE REGEX)
    # =========================================
    if "open notepad" in cmd or "launch notepad" in cmd: return {"app": "notepad", "action": "open"}
    elif "close notepad" in cmd or "exit notepad" in cmd: return {"app": "notepad", "action": "close"}

    match_write = re.search(r"(?:write|type|add|say) (.*)", raw_text_command, re.IGNORECASE)
    if match_write: return {"app": result["app"] or "notepad", "action": "write", "text": match_write.group(1).strip()}

    match_save = re.search(r"save(?: it| file)?(?: as| called| named)? (.*)", raw_text_command, re.IGNORECASE)
    if match_save:
        filename = match_save.group(1).strip().replace(".", "").replace(",", "")
        if not filename.endswith(".txt"): filename += ".txt"
        return {"app": result["app"] or "notepad", "action": "save", "text": filename}
    elif "save" in cmd: return {"app": result["app"] or "notepad", "action": "save", "text": "test.txt"}

    match_replace = re.search(r"(?:replace|change|swap|turn) (.*?) (?:with|to|for|into) (.*)", cmd)
    if match_replace: return {"app": result["app"] or "notepad", "action": "replace", "old_text": match_replace.group(1).strip(), "new_text": match_replace.group(2).strip()}

    match_del_line_word = re.search(r"(?:delete|remove) word (.*?) from line (\d+)", cmd)
    if match_del_line_word: return {"app": result["app"] or "notepad", "action": "delete", "text": match_del_line_word.group(1).strip(), "line": int(match_del_line_word.group(2))}
    
    match_del_line = re.search(r"(?:delete|remove) line (\d+)", cmd)
    if match_del_line: return {"app": result["app"] or "notepad", "action": "delete_line", "line": int(match_del_line.group(1))}
    
    match_del_word = re.search(r"(?:delete|remove)(?: word)? (.*)", cmd)
    if match_del_word: return {"app": result["app"] or "notepad", "action": "delete", "text": match_del_word.group(1).strip()}

    match_ins_line = re.search(r"(?:insert|add|put) (.*?) (?:at|on|in) line (\d+)", cmd)
    if match_ins_line: return {"app": result["app"] or "notepad", "action": "insert", "text": match_ins_line.group(1).strip(), "line": int(match_ins_line.group(2))}
    
    match_ins = re.search(r"(?:insert|add) (.*)", cmd)
    if match_ins: return {"app": result["app"] or "notepad", "action": "insert", "text": match_ins.group(1).strip()}

    if "undo" in cmd: return {"app": result["app"] or "notepad", "action": "undo"}
    elif "redo" in cmd: return {"app": result["app"] or "notepad", "action": "redo"}
    elif "new paragraph" in cmd: return {"app": result["app"] or "notepad", "action": "new_paragraph"}
    elif "new line" in cmd: return {"app": result["app"] or "notepad", "action": "new_line"}
    elif "space" in cmd: return {"app": result["app"] or "notepad", "action": "space"}
    elif "clear" in cmd or "empty" in cmd: return {"app": result["app"] or "notepad", "action": "clear"}
    elif "new tab" in cmd: return {"app": "notepad", "action": "new_tab"}
    elif "new file" in cmd: return {"app": "notepad", "action": "new"}
    elif "read" in cmd and "unread" not in cmd and "message" not in cmd: return {"app": result["app"] or "notepad", "action": "read"}

    # =========================================
    # 💬 SPOTIFY
    # =========================================
    if result["app"] == "spotify":
        
        mood_map = {
            "sad": ["sad", "low", "depressed", "heartbreak", "cry"],
            "party": ["party", "dance", "club", "vibes", "fun"],
            "chill": ["chill", "relax", "study", "lofi", "flow", "calm"],
            "romantic": ["love", "romantic", "date"],
            "energy": ["gym", "workout", "energy", "power"]
        }
        query_map = {
            "sad": "Sad Songs for Soul",
            "party": "Top Party Hits",
            "chill": "Lofi Hip Hop Radio - Beats to Relax/Study to",
            "romantic": "Romantic Evening Playlist",
            "energy": "High Energy Workout Mix"
        }

        for mood, keywords in mood_map.items():
            if any(word in cmd for word in keywords):
                return {"app": "spotify", "action": "play", "text": query_map[mood]}
        
        if "your mood" in cmd or "you like" in cmd: return {"app": "spotify", "action": "play", "text": "Sture Zetterberg Mix"}
        if "open" in cmd: return {"app": "spotify", "action": "open"}
        if "close" in cmd: return {"app": "spotify", "action": "close"}
   
    if "like" in cmd: return {"app": "spotify", "action": "like"} 

    match_play = re.search(r"(?:play|listen to) (.*?)(?: on spotify)?$", raw_text_command, re.IGNORECASE)
    if match_play:
        clean_song = match_play.group(1).strip()
        if clean_song: return {"app": "spotify", "action": "play", "text": clean_song}

    if "pause" in cmd: return {"app": "spotify", "action": "pause"}
    if "resume" in cmd or cmd == "play": return {"app": "spotify", "action": "resume"}
    if "next" in cmd: return {"app": "spotify", "action": "next"}
    if "previous" in cmd: return {"app": "spotify", "action": "previous"}
        
    # =========================================
    # 🧮 CALCULATOR 
    # =========================================
    if "open calculator" in cmd: return {"app": "calculator", "action": "open"}
    if "close calculator" in cmd: return {"app": "calculator", "action": "close"}
    
    if re.search(r"\b(square|root|factorial|pi|power)\b", cmd): return {"app": "calculator", "action": "calculate", "expression": None}
    
    match_calc = re.search(r"(?:calculate|what is|whats) (.*)", cmd)
    if match_calc or any(word in cmd for word in ["+", "-", "*", "/", "divide", "multiply"]):
        expr = match_calc.group(1) if match_calc else cmd
        expr = expr.replace("plus", "+").replace("minus", "-").replace("multiply", "*").replace("multiplied by", "*").replace("x", "*").replace("divide", "/").replace("divided by", "/")
        expr = re.sub(r"[a-zA-Z]", "", expr).strip()
        return {"app": "calculator", "action": "calculate", "expression": expr}
    
    # =========================================
    # 💬 WHATSAPP
    # =========================================
    if "open whatsapp" in cmd: return {"app": "whatsapp", "action": "open"}
    elif "close whatsapp" in cmd: return {"app": "whatsapp", "action": "close"}
    
    match_read_specific = re.search(r"(?:read|check)(?: my)? messages? from (.*)", cmd)
    if match_read_specific: return {"app": "whatsapp", "action": "read_specific", "contact": match_read_specific.group(1).strip()}
    
    elif "show unread" in cmd or "see unread" in cmd: return {"app": "whatsapp", "action": "show_unread"}
    
    match_voice_note = re.search(r"(?:send )?voice (?:message|note)(?: to)? (.*)", cmd)
    if match_voice_note: return {"app": "whatsapp", "action": "voice_note", "contact": match_voice_note.group(1).strip()}   
    
    elif "stop recording" in cmd or "stop voice" in cmd: return {"app": "whatsapp", "action": "stop_voice"}
    
    # "Send message to Shraddha saying hello there"
    # 🔥 THE FIX: Strips 'message to' or 'whatsapp to' from the contact name
    match_send_saying = re.search(r"(?:send|message|whatsapp)(?:\s+a\s+message)?(?:\s+to)?\s+(.*?)(?:\s+saying|\s+that\s+says|:|$) (.*)", raw_text_command, re.IGNORECASE)
    if match_send_saying:
        contact = match_send_saying.group(1).strip()
        # Remove 'message to' if it accidentally got caught
        contact = re.sub(r'^(message to|whatsapp to|to)\s+', '', contact, flags=re.IGNORECASE)
        return {"app": "whatsapp", "action": "send_to", "contact": contact, "text": match_send_saying.group(2).strip()}

    match_send = re.search(r"send message (.*)", raw_text_command, re.IGNORECASE)
    if match_send: return {"app": "whatsapp", "action": "send", "text": match_send.group(1).strip()}
    
    match_screenshot = re.search(r"send screenshot to (.*)", cmd)
    if match_screenshot: return {"app": "whatsapp", "action": "screenshot", "contact": match_screenshot.group(1).strip()}
    
    match_video_call = re.search(r"video call (.*)", cmd)
    if match_video_call: return {"app": "whatsapp", "action": "video_call", "contact": match_video_call.group(1).strip()}
    
    match_voice_call = re.search(r"(?:voice call|call) (.*)", cmd)
    if match_voice_call: return {"app": "whatsapp", "action": "voice_call", "contact": match_voice_call.group(1).strip()}
    
    if "status" in cmd: return {"app": "whatsapp", "action": "open_status", "contact": cmd.split()[-1]}
    
    match_contact_card = re.search(r"send contact (.*) to (.*)", cmd)
    if match_contact_card: return {"app": "whatsapp", "action": "send_contact_card", "share_name": match_contact_card.group(1).strip(), "target": match_contact_card.group(2).strip()}
    
    match_attachment = re.search(r"send (?:file|document|attachment) (.*) (?:from|in) (desktop|downloads|documents) to (.*)", cmd)
    if match_attachment: return {"app": "whatsapp", "action": "send_attachment", "file_name": match_attachment.group(1).strip(), "location": match_attachment.group(2).strip(), "contact": match_attachment.group(3).strip()}

    return result