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
    # 🔥 ONLY FALLBACK TO LLM IF ABSOLUTELY NOTHING DETECTED
    if not structured or structured.get("status") == "error":

        # 🔥 PREVENT LLM FOR SIMPLE COMMANDS
        simple_keywords = ["mute", "unmute", "volume", "play", "pause", "resume"]

        if any(k in command.lower() for k in simple_keywords):
            return {
                "status": "error",
                "response": "❌ Unknown command. Try:\n- mute yt\n- volume down yt\n- play song"
            }

        # 🔥 OTHERWISE USE LLM
        raw = llm.generate(command)

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
                "response": "❌ Sorry, I didn't understand that.\nTry commands like:\n- play song on yt\n- mute youtube\n- search something"
            }


    # 🔥 ADD ORIGINAL COMMAND (future-safe)
    # 🔥 TARGET + ACTION FINAL SANITIZATION (100% FIX)

    # 🔥 FINAL INTENT CORRECTION (ONLY ONE CLEAN BLOCK)

    valid_actions = [
        "open", "close", "search", "play_music",
        "pause", "resume", "stop",
        "mute", "unmute", "volume_up", "volume_down",
        "add_to_favorites", "remove_favorite",
        "play_favorite", "play_last", "play_yesterday",
        "send_file", "read_messages", "send_email",
        "handle_mood", "close_browser",
        "switch_back", "switch_to_google", "switch_to_app",
        "read_latest_email", "scroll",
        "skip_ad",
        "open_result_by_name"
    ]

    valid_targets = [
        "youtube", "spotify", "google", "gmail",
        "whatsapp", "browser"
    ]

    lower = command.lower()

    # 🔥 FORCE EMOTION FIRST (VERY IMPORTANT)
    if any(word in lower for word in [
        "sad", "terrible", "bad", "depressed",
        "lonely", "upset", "not okay"
    ]):
        structured = {
            "action": "handle_mood",
            "target": "youtube",
            "query": {"mood": "sad"}
        }

    # 🔥 FIX INVALID ACTION
    elif structured.get("action") and structured.get("action") not in valid_actions:
        structured = {
            "action": "search",
            "target": "google",
            "query": command
        }

    # 🔥 FIX INVALID TARGET
    # 🔥 FIX INVALID TARGET (DO NOT TOUCH None)
    if structured.get("target") is not None and structured.get("target") not in valid_targets:

        if "music" in lower or "song" in lower:
            structured["target"] = "youtube"

        elif "mail" in lower or "email" in lower:
            structured["target"] = "gmail"

        elif "whatsapp" in lower or "message" in lower:
            structured["target"] = "whatsapp"

        else:
            structured["target"] = "google"



    # 🔥 ADD ORIGINAL COMMAND AFTER FIX
    # 🔥 DO NOT overwrite for multi-intent
    if "actions" not in structured:
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

        if not result:
            print("Assistant: ❌ Something went wrong.")
        else:
            print("Assistant:", result.get("response", "❌ No response"))