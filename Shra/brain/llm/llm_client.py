import requests
import json


class LLMClient:

    def __init__(self, model="gemma3:4b"):
        self.model = model
        self.url = "http://localhost:11434/api/generate"

    def generate(self, prompt: str):
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }

            response = requests.post(self.url, json=payload)

            if response.status_code != 200:
                raise Exception(f"Ollama error: {response.text}")

            data = response.json()
            return data["response"]

        except Exception as e:
            print("FULL LLM ERROR:", str(e))
            raise