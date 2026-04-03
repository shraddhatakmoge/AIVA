"""
Main Entry Point for AIVA Browser Automation Backend

This file exposes a single function:

    process_command(command: str) -> dict

Your UI friend should import and use this function.

It also supports optional CLI mode for standalone testing.
"""

from AIVA.Shra.features.browser.controller import BrowserController
from AIVA.Shra.brain.simple_command_parser import SimpleCommandParser

# -------------------------------------------------
# Initialize Core Engine (Singleton Style)
# -------------------------------------------------
browser = BrowserController()
parser = SimpleCommandParser()


# -------------------------------------------------
# PUBLIC FUNCTION FOR UI
# -------------------------------------------------
def process_command(command: str) -> dict:
    """
    Main function to process a user command.

    Args:
        command (str): Natural language command

    Returns:
        dict: {
            "status": "success" | "error",
            "response": str
        }
    """

    if not command or not isinstance(command, str):
        return {
            "status": "error",
            "response": "Invalid command."
        }

    # Parse command
    structured = parser.parse(command)

    if not structured:
        return {
            "status": "error",
            "response": "Could not understand command."
        }

    # Execute command
    result = browser.handle(structured)

    return result


# -------------------------------------------------
# OPTIONAL CLI MODE (For Local Testing Only)
# -------------------------------------------------
if __name__ == "__main__":

    print("AIVA Browser Automation CLI")
    print("Type 'exit' to quit.\n")

    while True:
        command = input("Enter command: ")

        if command.lower() in ["exit", "quit"]:
            print("Exiting AIVA.")
            break

        result = process_command(command)
        print(result)
        print()