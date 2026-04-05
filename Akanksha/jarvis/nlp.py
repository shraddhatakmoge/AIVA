import re
import os


# 🔥 Notice we added 'current_app' to the function arguments
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
    
    if "word" in cmd or "ms word" in cmd:
        result["app"] = "word"
    elif "spotify" in cmd or "music" in cmd or "song" in cmd:
        result["app"] = "spotify"
    elif "calculator" in cmd or "calculate" in cmd or "+" in cmd or "-" in cmd or "*" in cmd or "/" in cmd:
        result["app"] = "calculator"
    elif "whatsapp" in cmd or "message" in cmd or "call" in cmd:
        result["app"] = "whatsapp"
    elif "folder" in cmd or "find file" in cmd or "search for" in cmd:
        result["app"] = "file_system"
    elif "notepad" in cmd:
         result["app"] = "notepad"
    else:
        # 🔥 THE MAGIC TRICK: If they didn't specify an app, use the Memory!
        result["app"] = current_app


    # -----------------------------------------
    # 📄 MS WORD LOGIC
    # -----------------------------------------
    if result["app"] == "word":
        
        # 1. Open App vs Open File
        if "open file" in cmd or "open document" in cmd:
            result["action"] = "open_file"
            
            # Grab location if specified
            if "desktop" in cmd: result["folder"] = "desktop"
            elif "documents" in cmd: result["folder"] = "documents"
            elif "downloads" in cmd: result["folder"] = "downloads"
            
            # Clean up the sentence to isolate the filename
            clean_cmd = cmd.replace("open file", "").replace("open document", "").replace("in word", "")
            for loc in ["from desktop", "on desktop", "in documents", "from documents", "in downloads", "from downloads"]:
                clean_cmd = clean_cmd.replace(loc, "")
            
            result["text"] = clean_cmd.strip()

        # Just open the app
        elif "open" in cmd and "file" not in cmd and "document" not in cmd: 
            result["action"] = "open"
            
        # 2. Close App
        elif "close" in cmd: 
            result["action"] = "close"
        elif "new document" in cmd or "new file" in cmd: result["action"] = "new"
            
        elif "write" in cmd or "type" in cmd:
            result["action"] = "write"
            # Remove "write" and "in word"
            text = re.sub(r'^(write|type)\s+', '', raw_text_command, flags=re.IGNORECASE)
            result["text"] = re.sub(r'(?i)\s+in word$', '', text).strip()
            
        elif "save" in cmd:
            result["action"] = "save"
            
            # 🔥 SMART LOCATION FIX: Check for OneDrive first!
            if "desktop" in cmd:
                onedrive_desktop = os.path.expanduser("~\\OneDrive\\Desktop")
                local_desktop = os.path.expanduser("~\\Desktop")
                # Route to OneDrive if it exists, otherwise use Local
                result["folder"] = onedrive_desktop if os.path.exists(onedrive_desktop) else local_desktop
                
            elif "documents" in cmd:
                onedrive_docs = os.path.expanduser("~\\OneDrive\\Documents")
                local_docs = os.path.expanduser("~\\Documents")
                result["folder"] = onedrive_docs if os.path.exists(onedrive_docs) else local_docs
            
            match = re.search(r"save (?:it |file )?(?:as|called|with name)? (.*?)(?: in| to| on|$)", cmd)
            if match:
                filename = match.group(1).strip()
                if not filename.endswith(".docx"): filename += ".docx"
                result["text"] = filename
            else:
                result["text"] = "Document.docx"
                
        elif "heading" in cmd:
            result["action"] = "heading"
            match = re.search(r"heading (\d)", cmd)
            result["level"] = int(match.group(1)) if match else 1
            
        # 🔥 SPECIFIC STYLING (MUST BE ABOVE GENERIC STYLING)
    
        # 🔥 SMART SPECIFIC STYLING (Handles Color, Size, and Style together)
        elif "make the word" in cmd or "make word" in cmd or "make the words" in cmd:
            result["action"] = "style_specific"
            
            # 1. Isolate the target word
            # We split the sentence at the first style/color/size word we see
            parts = re.split(r'\b(bold|italic|underline|red|blue|green|yellow|black|white|purple|pink|orange|size)\b', cmd)
            
            if len(parts) > 1:
                # The target word is whatever comes before the styling words
                prefix = parts[0]
                target = re.sub(r".*make (?:the )?words?\s+", "", prefix).strip()
                result["text"] = target
                
                # 2. Scan for Basic Styles
                if "bold" in cmd: result["style"] = "bold"
                elif "italic" in cmd: result["style"] = "italic"
                elif "underline" in cmd: result["style"] = "underline"
                
                # 3. Scan for Colors
                colors = ["red", "blue", "green", "yellow", "black", "white", "purple", "pink", "orange"]
                for c in colors:
                    if c in cmd:
                        result["color"] = c
                        break
                        
                # 4. Scan for Size
                size_match = re.search(r"size (\d+)", cmd)
                if size_match:
                    result["size"] = int(size_match.group(1))

        # 🎨 GENERIC STYLING
        elif "bold" in cmd:
            result["action"] = "style"; result["style"] = "bold"
        elif "italic" in cmd:
            result["action"] = "style"; result["style"] = "italic"
        elif "underline" in cmd:
            result["action"] = "style"; result["style"] = "underline"
            
        # 📐 ALIGNMENT
        elif "align center" in cmd or "center align" in cmd:
            result["action"] = "alignment"; result["align"] = "center"
        elif "align right" in cmd or "right align" in cmd:
            result["action"] = "alignment"; result["align"] = "right"
        elif "align left" in cmd or "left align" in cmd:
            result["action"] = "alignment"; result["align"] = "left"
        elif "justify" in cmd:
            result["action"] = "alignment"; result["align"] = "justify"
            
            
        # --- ADVANCED FEATURES (Ported from Notepad) ---
        elif "clear" in cmd or "empty" in cmd: result["action"] = "clear"
        elif "read" in cmd: result["action"] = "read"
        elif "new paragraph" in cmd: result["action"] = "new_paragraph"
        elif "new line" in cmd: result["action"] = "new_line"
        elif cmd == "space" or "add space" in cmd: result["action"] = "space"

        elif "delete word" in cmd:
            result["action"] = "delete"
            result["text"] = cmd.split("delete word")[-1].strip()

        elif "insert" in cmd or "add" in cmd or "put" in cmd:
            match_ins_line = re.search(r"(?:insert|add|put) (.*?) (?:at|on|in) line (\d+)", cmd)
            if match_ins_line:
                result["action"] = "insert"
                result["text"] = match_ins_line.group(1).strip()
                result["line"] = int(match_ins_line.group(2))
            else:
                text = cmd.replace("insert", "").replace("add", "").strip()
                result["action"] = "insert"
                result["text"] = text

        elif "replace" in cmd or "change" in cmd:
            match_replace = re.search(r"(?:replace|change) (.*?) (?:with|to) (.*)", cmd)
            if match_replace:
                result["action"] = "replace"
                result["old_text"] = match_replace.group(1).strip()
                result["new_text"] = match_replace.group(2).strip()

        elif "move" in cmd:
            for direction in ["left", "right", "up", "down"]:
                if direction in cmd:
                    result["action"] = "move"
                    result["direction"] = direction

        return result

    # -----------------------------------------
    # 📝 NOTEPAD LOGIC (Fallback if no app defined)
    # -----------------------------------------
    # If the user didn't specify an app, or explicitly said notepad, assume Notepad.
    if result["app"] == "notepad" or result["app"] is None:
        result["app"] = "notepad"

        if "open" in cmd: result["action"] = "open"
        elif "close" in cmd: result["action"] = "close"
        elif "new file" in cmd: result["action"] = "new"
        elif "clear" in cmd or "empty" in cmd: result["action"] = "clear"
        elif "read" in cmd: result["action"] = "read"
        elif "undo" in cmd: result["action"] = "undo"
        elif "redo" in cmd: result["action"] = "redo"
        elif "new paragraph" in cmd: result["action"] = "new_paragraph"
        elif "new line" in cmd: result["action"] = "new_line"
        elif cmd == "space" or "add space" in cmd: result["action"] = "space"
        elif "delete line" in cmd: result["action"] = "delete_line"

        elif "write" in cmd or "type" in cmd:
            result["action"] = "write"
            # Remove "write" and "in notepad"
            text = re.sub(r'^(write|type)\s+', '', raw_text_command, flags=re.IGNORECASE)
            result["text"] = re.sub(r'(?i)\s+in notepad$', '', text).strip()

        elif "save" in cmd:
            result["action"] = "save"
            match_save = re.search(r"save (?:it |file )?(?:as|called|with name)? (.*)", raw_text_command, re.IGNORECASE)
            if match_save:
                filename = match_save.group(1).strip().replace(".", "").replace(",", "")
                if not filename.endswith(".txt"): filename += ".txt"
                result["text"] = filename
            else:
                result["text"] = "test.txt"

        elif "delete word" in cmd:
             if "line" in cmd:
                 match = re.search(r"delete word (.*?) from line (\d+)", cmd)
                 if match:
                     result["action"] = "delete"
                     result["text"] = match.group(1).strip()
                     result["line"] = int(match.group(2))
             else:
                 result["action"] = "delete"
                 result["text"] = cmd.split("delete word")[-1].strip()

        elif "insert" in cmd or "add" in cmd or "put" in cmd:
             match_ins_line = re.search(r"(?:insert|add|put) (.*?) (?:at|on|in) line (\d+)", cmd)
             if match_ins_line:
                 result["action"] = "insert"
                 result["text"] = match_ins_line.group(1).strip()
                 result["line"] = int(match_ins_line.group(2))
             else:
                 text = cmd.replace("insert", "").replace("add", "").strip()
                 result["action"] = "insert"
                 result["text"] = text

        elif "replace" in cmd or "change" in cmd:
             match_replace = re.search(r"(?:replace|change) (.*?) (?:with|to) (.*)", cmd)
             if match_replace:
                 result["action"] = "replace"
                 result["old_text"] = match_replace.group(1).strip()
                 result["new_text"] = match_replace.group(2).strip()

        elif "move" in cmd:
            for direction in ["left", "right", "up", "down"]:
                if direction in cmd:
                    result["action"] = "move"
                    result["direction"] = direction

        return result

    # =========================================
    # 📝 UPDATED NOTEPAD LOGIC
    # =========================================
    # For WRITE/TYPE, use raw_text_command to preserve capitals
    if ("write" in cmd or "type" in cmd):
        # Remove the word 'write' or 'type' but keep the rest of the casing
        text_to_write = re.sub(r'^(write|type|add)\s+', '', raw_text_command, flags=re.IGNORECASE).strip()
        
        # 🔥 THE FIX: Use result["app"] so it respects your Context Memory!
        return {"app": result["app"], "action": "write", "text": text_to_write}

    # For SAVE, use raw_text_command (In case they want a Capitalized filename)
    match_save = re.search(r"save (?:as|file|file called|it as) (.*)", raw_text_command, re.IGNORECASE)
    if match_save:
        # 🔥 THE FIX: Use result["app"] here too!
        return {"app": result["app"], "action": "save", "text": match_save.group(1).strip()}


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
    
    # =========================================
    # 📝 FULL SMART NOTEPAD NLP (16 FEATURES)
    # =========================================

    # 1 & 2. OPEN / CLOSE
    if "open notepad" in cmd:
        return {"app": "notepad", "action": "open"}
    elif "close notepad" in cmd:
        return {"app": "notepad", "action": "close"}

    # 4. SMART SAVE (Handles: "save as report", "save file test")
    # 💾 SMART SAVE (High Priority)
    # This must come BEFORE any simple "if 'save' in cmd" check
    match_save = re.search(r"save (?:it |file )?(?:as|called|with name)? (.*)", raw_text_command, re.IGNORECASE)
    
    if match_save:
        filename = match_save.group(1).strip()
        # Clean up any leftover punctuation from the sentence split
        filename = filename.replace(".", "").replace(",", "").strip()
        if not filename.endswith(".txt"): 
            filename += ".txt"
        return {"app": "notepad", "action": "save", "text": filename}

    # Fallback only if no filename is provided
    elif "save" in cmd:
        return {"app": "notepad", "action": "save", "text": "test.txt"}

    # 11. DELETE WORD FROM LINE (Priority Check)
    match_del_line = re.search(r"delete word (.*?) from line (\d+)", cmd)
    if match_del_line:
        return {"app": "notepad", "action": "delete", "text": match_del_line.group(1).strip(), "line": int(match_del_line.group(2))}

    # 5 & 9. DELETE LINE / DELETE WORD
    elif "delete line" in cmd:
        return {"app": "notepad", "action": "delete_line"}
    elif "delete word" in cmd:
        return {"app": "notepad", "action": "delete", "text": cmd.split("delete word")[-1].strip()}

    # 14. INSERT TEXT AT LINE
    match_ins_line = re.search(r"(?:insert|add|put) (.*?) (?:at|on|in) line (\d+)", cmd)
    if match_ins_line:
        return {"app": "notepad", "action": "insert", "text": match_ins_line.group(1).strip(), "line": int(match_ins_line.group(2))}

    # 8. REPLACE WORD
    match_replace = re.search(r"(?:replace|change) (.*?) (?:with|to) (.*)", cmd)
    if match_replace:
        return {"app": "notepad", "action": "replace", "old_text": match_replace.group(1).strip(), "new_text": match_replace.group(2).strip()}

    # 10. UNDO / REDO
    if "undo" in cmd:
        return {"app": "notepad", "action": "undo"}
    elif "redo" in cmd:
        return {"app": "notepad", "action": "redo"}

    # 12. NEW LINE / PARAGRAPH
    if "new paragraph" in cmd:
        return {"app": "notepad", "action": "new_paragraph"}
    elif "new line" in cmd:
        return {"app": "notepad", "action": "new_line"}

    # 13. CURSOR MOVEMENT
    if "move" in cmd:
        for direction in ["left", "right", "up", "down"]:
            if direction in cmd:
                return {"app": "notepad", "action": "move", "direction": direction}

    # 16. SPACE (Added)
    elif cmd == "space" or "add space" in cmd:
        return {"app": "notepad", "action": "space"}

    # 15. INSERT AT CURSOR (Generic Add/Insert)
    if "insert" in cmd or "add" in cmd:
        text = cmd.replace("insert", "").replace("add", "").strip()
        return {"app": "notepad", "action": "insert", "text": text}

    # 3. WRITE / TYPE
    # Inside your nlp.py Notepad section
    if "write" in cmd or "type" in cmd:
        # Use a regex that ONLY removes the trigger word at the start
        text_to_write = re.sub(r'^(write|type|add)\s+', '', raw_text_command, flags=re.IGNORECASE).strip()
        return {"app": "notepad", "action": "write", "text": text_to_write}

    # 5. CLEAR / 6. NEW FILE / 7. READ
    if "clear" in cmd or "empty" in cmd:
        return {"app": "notepad", "action": "clear"}
    elif "new file" in cmd or "create file" in cmd:
        return {"app": "notepad", "action": "new"}
    elif "read" in cmd:
        return {"app": "notepad", "action": "read"}
    
    # =========================================
    # 📝 NATURAL LANGUAGE NOTEPAD
    # =========================================

    # ✍️ WRITE (Natural: "say hello", "tell him i am coming", "type something")
    match_write = re.search(r"(?:write|type|say|tell him|tell her) (.*)", cmd)
    if match_write and "line" not in cmd and "save" not in cmd:
        return {"app": "notepad", "action": "write", "text": match_write.group(1).strip()}

    # 💾 SAVE (Natural: "save it", "save as notes", "call the file x")
    match_save = re.search(r"save (?:it |file )?(?:as|called|with name)? (.*)", cmd)
    if match_save:
        filename = match_save.group(1).strip()
        if not filename.endswith(".txt"): filename += ".txt"
        return {"app": "notepad", "action": "save", "text": filename}

    # 🔄 REPLACE (Natural: "swap x for y", "turn x into y")
    match_swap = re.search(r"(?:swap|turn|change) (.*?) (?:for|into|to) (.*)", cmd)
    if match_swap:
        return {"app": "notepad", "action": "replace", "old_text": match_swap.group(1).strip(), "new_text": match_swap.group(2).strip()}

    # ➕ INSERT (Natural: "put x on line y", "squeeze x into line y")
    match_put = re.search(r"(?:put|squeeze|insert|add) (.*?) (?:on|at|into) line (\d+)", cmd)
    if match_put:
        return {"app": "notepad", "action": "insert", "text": match_put.group(1).strip(), "line": int(match_put.group(2))}

    # =========================================
    # 📂 FILE & FOLDER OPERATIONS (NEW)
    # =========================================
    
    # 📁 CREATE FOLDER
    if "create folder" in cmd or "make folder" in cmd:
        name = cmd.replace("create folder", "").replace("make folder", "").strip()
        return {
            "app": "file_system",
            "intent": "create_folder",
            "entities": {"path": name}
        }

    # 📄 CREATE FILE
    elif "create file" in cmd:
        name = cmd.replace("create file", "").strip()
        return {
            "app": "file_system",
            "intent": "create_file",
            "entities": {"path": name}
        }

    # 🔍 SEARCH FILE
    elif "search for" in cmd or "find file" in cmd:
        name = cmd.replace("search for", "").replace("find file", "").strip()
        return {
            "app": "file_system",
            "intent": "search_file",
            # We default to searching the whole User directory if not specified
            "entities": {"filename": name, "directory": os.path.expanduser("~")}
        }

    # 🗑️ DELETE FILE/FOLDER
    elif "delete" in cmd and ("file" in cmd or "folder" in cmd):
        name = cmd.replace("delete file", "").replace("delete folder", "").strip()
        intent = "delete_file" if "file" in cmd else "delete_folder"
        return {
            "app": "file_system",
            "intent": intent,
            "entities": {"path": name}
        }
  




    # DEFAULT APP FALLBACK
    if result["app"] is None:
        result["app"] = "notepad"

    return result