class Memory:

    def __init__(self):
        self.last_intent = None
        self.last_platform = None
        self.last_query = None

    def update(self, data: dict):
        self.last_intent = data.get("intent")
        self.last_platform = data.get("platform")
        self.last_query = data.get("query")

    def get_context(self):

        if not self.last_intent:
            return ""

        return f"""
Last intent: {self.last_intent}
Last platform: {self.last_platform}
Last query: {self.last_query}
"""