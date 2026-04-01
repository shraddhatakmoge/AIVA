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
                        "content": """You are an AI assistant that ONLY returns JSON.

STRICT RULES:
- ALWAYS return valid JSON
- ALWAYS include: action
- DO NOT explain anything
- DO NOT use markdown
- DO NOT skip keys

Example:
{"action": "play", "target": "youtube", "query": "song name"}
"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "stream": False
            }

            response = requests.post(self.url, json=payload)

            if response.status_code != 200:
                raise Exception(f"Ollama error: {response.text}")

            data = response.json()
            content = data["message"]["content"]

            # 🔥 CLEAN MARKDOWN
            content = re.sub(r"```json|```", "", content).strip()

            # 🔥 FIX SINGLE QUOTES (phi3 issue)
            if content.startswith("{") and "'" in content:
                content = content.replace("'", '"')

            # 🔥 RETURN STRING (IMPORTANT — SAME AS GEMMA)
            return content

        except Exception as e:
            print("FULL LLM ERROR:", str(e))
            return ""