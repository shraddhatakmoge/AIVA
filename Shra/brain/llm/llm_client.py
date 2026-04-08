import requests
import json
import re


class LLMClient:

    def __init__(self, model="phi3"):
        self.model = model
        self.url = "http://localhost:11434/api/chat"

    def generate(self, prompt: str):
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": """
    You are a STRICT JSON command generator.

    ONLY return JSON. NOTHING ELSE.

    Allowed actions:
    open, close, search, play_music,
    pause, resume, stop,
    add_to_favorites, remove_favorite,
    play_favorite, play_last, play_yesterday,
    send_file, read_messages, send_email,
    handle_mood

    Rules:
    - Output MUST be valid JSON
    - NO explanations
    - NO extra text
    - NO markdown
    - NO examples
    - NO multiple languages

    If emotion detected:
    → action = "handle_mood"

    If unclear:
    → action = "search", target = "google", query = user input

    Correct format:
    {"action":"play_music","target":"youtube","query":"song"}
    """
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "stream": False,
                "options": {
                    "temperature": 0  # 🔥 VERY IMPORTANT
                }
            }

            response = requests.post(self.url, json=payload)

            data = response.json()
            content = data["message"]["content"]

            # 🔥 HARD CLEAN
            content = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
            content = content.strip()

            # 🔥 EXTRACT ONLY FIRST JSON
            match = re.search(r"\{.*?\}", content, re.DOTALL)
            if not match:
                print("LLM RAW:", content)
                return {}

            json_str = match.group()

            # 🔥 FIX INVALID JSON (single quotes, bad format)
            try:
                return json.loads(json_str)
            except:
                try:
                    fixed = json_str.replace("'", '"')
                    return json.loads(fixed)
                except:
                    print("BROKEN JSON:", json_str)

                    # 🔥 FINAL FALLBACK (VERY IMPORTANT)
                    return {
                        "action": "search",
                        "target": "google",
                        "query": prompt
                    }
        except Exception as e:
            print("LLM ERROR:", str(e))
            return {}