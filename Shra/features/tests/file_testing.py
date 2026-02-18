from features.file_manager.file_service import handle_file_command


def simple_intent_parser(text):
    text = text.lower()

    if text.startswith("create file"):
        filename = text.replace("create file", "").strip()
        return "create_file", {"path": filename}

    elif text.startswith("delete file"):
        filename = text.replace("delete file", "").strip()
        return "delete_file", {"path": filename}

    elif text.startswith("read file"):
        filename = text.replace("read file", "").strip()
        return "read_file", {"path": filename}

    else:
        return None, None


def main():
    print("Voice Simulation Mode (type command)")

    while True:
        user_input = input("\nYou: ")

        if user_input.lower() == "exit":
            break

        intent, entities = simple_intent_parser(user_input)

        if intent:
            response = handle_file_command(intent, entities)
            print("Assistant:", response["message"])
        else:
            print("Assistant: Sorry, I didn't understand.")


if __name__ == "__main__":
    main()
