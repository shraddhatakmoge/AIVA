import json
import re


class ResponseParser:

    @staticmethod
    def parse(raw_response: str):

        try:
            # Extract JSON block even if wrapped in ```json
            match = re.search(r"\{.*\}", raw_response, re.DOTALL)
            if not match:
                return {"status": "error", "response": "Invalid LLM output"}

            data = json.loads(match.group())

            # 🔥 NORMALIZATION LAYER (IMPORTANT)
            structured = {
                "action": data.get("action"),
                "target": data.get("target"),
                "query": data.get("query")
            }

            return structured

        except Exception as e:
            return {
                "status": "error",
                "response": f"Parsing failed: {str(e)}"
            }