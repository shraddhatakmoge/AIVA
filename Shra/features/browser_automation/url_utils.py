def clean_command(command: str) -> str:
    """
    Normalize command:
    - Convert to lowercase
    - Strip extra spaces
    """
    return command.lower().strip()


def remove_words(command: str, words_to_remove: list) -> str:
    """
    Safely remove full words only (no partial string cutting).
    Example:
        "play closer song on youtube"
    becomes:
        "closer"
    """

    words = command.split()

    # Remove only exact word matches
    filtered_words = [
        word for word in words
        if word not in words_to_remove
    ]

    return " ".join(filtered_words)
