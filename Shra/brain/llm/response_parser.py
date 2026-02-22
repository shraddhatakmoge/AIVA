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

            return data

        except Exception as e:
            return {
                "status": "error",
                "response": f"Parsing failed: {str(e)}"
            }