import json
import re


class ResponseParser:

    @staticmethod
    def parse(raw_response: str):

        try:
            raw_lower = raw_response.lower()

            # 🔥 DIRECT COMMAND OVERRIDE (CRITICAL FIX)
            match_open = re.search(
                r"open (.+?) (one|first|1|two|second|2|three|third|3)",
                raw_lower
            )

            if match_open:
                name = match_open.group(1).strip()
                rank = match_open.group(2)

                index_map = {
                    "one": 1, "first": 1, "1": 1,
                    "two": 2, "second": 2, "2": 2,
                    "three": 3, "third": 3, "3": 3
                }

                print("🔥 RESPONSE PARSER OVERRIDE:", name, index_map[rank])

                return {
                    "action": "open_result_by_name",
                    "target": "google",
                    "query": {
                        "name": name,
                        "index": index_map[rank]
                    },
                    "original_command": raw_response  # 🔥 CRITICAL FIX
                }
            # ---------------- NORMAL FLOW ----------------

            match = re.search(r"\{.*\}", raw_response, re.DOTALL)
            if not match:
                return {"status": "error", "response": "Invalid LLM output"}

            data = json.loads(match.group())

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