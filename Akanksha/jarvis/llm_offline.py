import ollama
import json
import re


def process_with_llm(command):

    prompt = f"""
You are a command parser.

Convert the user command into VALID JSON.

Rules:
- Output ONLY JSON
- No explanation
- No extra text
- No ``` blocks
- No comments
- If command mentions a person, put it in "contact"

Command: {command}

Output format:
{{
    "app": "notepad/whatsapp/word/spotify",
    "action": "open/write/insert/delete/move/read/save/send/open_status/voice_call/video_call",
    "text": "",
    "contact": "",
    "line": 0,
    "direction": ""
}}
"""

    try:
        response = ollama.chat(
            model='tinyllama',
            messages=[{"role": "user", "content": prompt}],
            options={
                "temperature": 0,
                "num_predict": 150
            }
        )
    except Exception as e:
        print("❌ Ollama error:", e)
        return {}

    result = response['message']['content']

    clean = result.strip()
    clean = clean[:clean.rfind("}")+1]   # 🔥 important fix

# 🔥 FIND ALL JSON BLOCKS
    matches = re.findall(r"\{[\s\S]*?\}", clean)

    if not matches:
        print("❌ No JSON found")
        print("RAW OUTPUT:", result)
        return {}

# 🔥 TRY EACH JSON UNTIL ONE WORKS
    for candidate in reversed(matches):  # try from last (most accurate)

    # FIX common issues
        candidate = re.sub(r",\s*}", "}", candidate)
        candidate = re.sub(r",\s*]", "]", candidate)
        candidate = candidate.replace("'", '"')

    # 🔥 REMOVE BAD LINES (NON-JSON)
        lines = candidate.split("\n")
        cleaned_lines = []

        for line in lines:
            line = line.strip()

        # keep only valid JSON-like lines
            if (
                ":" in line or
                line.startswith("{") or
                line.startswith("}") 
            ):
                cleaned_lines.append(line)

        candidate = "\n".join(cleaned_lines)

        try:
            return json.loads(candidate)
        except:
            continue

    print("❌ JSON still invalid")
    print("RAW OUTPUT:", result)
    return {}