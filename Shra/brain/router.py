class Router:

    def route(self, parsed_data):

        # If parsing already failed
        if isinstance(parsed_data, dict) and parsed_data.get("status") == "error":
            return parsed_data

        # Ensure structured format
        return {
            "action": parsed_data.get("action"),
            "target": parsed_data.get("target"),
            "query": parsed_data.get("query", None)
        }