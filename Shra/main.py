"""
Main Entry Point for AIVA Browser Automation Backend

Expose this function to your friend:

    process_command(command: str) -> dict
"""

from AIVA.Shra.features.browser.controller import BrowserController
from AIVA.Shra.brain.simple_command_parser import SimpleCommandParser
from AIVA.Shra.brain.llm.llm_client import LLMClient
from AIVA.Shra.brain.llm.response_parser import ResponseParser

# 🔥 SINGLETON INSTANCES (important for session continuity)
browser = BrowserController()
parser = SimpleCommandParser()

# 🔥 LLM INSTANCE
llm = LLMClient()


def process_command(command: str) -> dict:
    """
    Main function to process user commands.

    Args:
        command (str): Natural language input

    Returns:
        dict:
        {
            "status": "success" | "error" | "ask",
            "response": str
        }
    """

    # 🔥 BASIC VALIDATION
    if not command or not isinstance(command, str):
        return {
            "status": "error",
            "response": "Invalid command."
        }

    # 🔥 EMAIL CONTINUATION FLOW (VERY IMPORTANT)
    if browser.pending_email:
        try:
            return browser.handle({
                "action": "continue_email",
                "query": command
            })
        except Exception as e:
            return {
                "status": "error",
                "response": str(e)
            }

    # 🔥 PARSE COMMAND (RULE-BASED FIRST)
    structured = parser.parse(command)

    # 🔥 LLM FALLBACK (CLEAN + CORRECT)
    if (
        not structured
        or structured.get("status") == "error"
        or not structured.get("action")
    ):

        raw = llm.generate(command)

        if not raw:
            return {
                "status": "error",
                "response": "Could not understand command."
            }

        # 🔥 PARSE LLM OUTPUT (CORRECT)
        if isinstance(raw, dict):
            structured = raw
        else:
            structured = ResponseParser.parse(raw)

        # 🔥 FINAL SAFETY CHECK
        if not structured or not structured.get("action"):
            return {
                "status": "error",
                "response": "Could not understand command."
            }

    # 🔥 ADD ORIGINAL COMMAND (future-safe)
    structured["original_command"] = command

    # 🔥 SAFE EXECUTION (no crashes in UI)
    try:
        result = browser.handle(structured)
    except Exception as e:
        return {
            "status": "error",
            "response": str(e)
        }

    return result


# -------------------------------------------------
# OPTIONAL CLI MODE (FOR YOUR TESTING ONLY)
# -------------------------------------------------
if __name__ == "__main__":

    print("AIVA CLI Mode (type 'exit' to quit)\n")

    while True:
        command = input("You: ")

        if command.lower() in ["exit", "quit"]:
            print("Exiting...")
            break

        result = process_command(command)
        print("Assistant:", result["response"])