"""
Browser Automation Testing File
--------------------------------
This file is ONLY for testing browser automation module.

It directly calls:
    handle_web_command()

All routing logic lives in:
    browser_automation/web_handler.py
"""

from features.browser_automation.web_handler import handle_web_command


def show_help():
    print("\n=== AIVA Browser Automation Test Mode ===\n")

    print("Open App Examples:")
    print("  open youtube")
    print("  open spotify")
    print("  open gmail")
    print("  open whatsapp")
    print("  open google\n")

    print("Play Examples:")
    print("  play believer on spotify")
    print("  play closer on youtube")
    print("  spotify play shape of you\n")

    print("Search Examples:")
    print("  search artificial intelligence")
    print("  search ai roadmap\n")

    print("Mail Example:")
    print("  send mail to test@gmail.com subject hello body how are you\n")

    print("WhatsApp Example:")
    print("  send whatsapp to Rahul hello bro\n")

    print("Type 'help' to show this message.")
    print("Type 'exit' to quit.\n")


if __name__ == "__main__":

    print("=== Browser Automation Testing Started ===")
    show_help()

    while True:
        command = input(">>> ")

        if command.lower().strip() == "exit":
            print("Exiting Browser Test Mode.")
            break

        if command.lower().strip() == "help":
            show_help()
            continue

        handle_web_command(command)
