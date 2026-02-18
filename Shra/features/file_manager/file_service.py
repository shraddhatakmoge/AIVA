import os

from .file_operations import (
    create_file,
    delete_file,
    rename_file,
    move_file,
    copy_file,
    read_file
)

from .folder_operations import (
    create_folder,
    delete_folder,
    rename_folder
)

from .search_operations import (
    search_by_name,
    search_by_extension
)


def resolve_path(path):
    """
    If user provides only filename (no absolute path),
    default location = Documents folder.
    """
    if not os.path.isabs(path):
        documents_dir = os.path.join(os.path.expanduser("~"), "Documents")
        return os.path.join(documents_dir, path)

    return path


def handle_file_command(intent, entities):

    try:

        if intent == "create_file":
            path = resolve_path(entities["path"])
            return create_file(path, entities.get("content", ""))

        elif intent == "delete_file":
            path = resolve_path(entities["path"])
            return delete_file(path)

        elif intent == "rename_file":
            old_path = resolve_path(entities["old_path"])
            new_path = resolve_path(entities["new_path"])
            return rename_file(old_path, new_path)

        elif intent == "move_file":
            source = resolve_path(entities["source"])
            destination = resolve_path(entities["destination"])
            return move_file(source, destination)

        elif intent == "copy_file":
            source = resolve_path(entities["source"])
            destination = resolve_path(entities["destination"])
            return copy_file(source, destination)

        elif intent == "read_file":
            path = resolve_path(entities["path"])
            return read_file(path)

        elif intent == "create_folder":
            path = resolve_path(entities["path"])
            return create_folder(path)

        elif intent == "delete_folder":
            path = resolve_path(entities["path"])
            return delete_folder(path)

        elif intent == "rename_folder":
            old_path = resolve_path(entities["old_path"])
            new_path = resolve_path(entities["new_path"])
            return rename_folder(old_path, new_path)

        elif intent == "search_file":
            directory = resolve_path(entities["directory"])
            return search_by_name(directory, entities["filename"])

        elif intent == "search_extension":
            directory = resolve_path(entities["directory"])
            return search_by_extension(directory, entities["extension"])

        else:
            return {
                "status": "error",
                "message": f"Unknown file command: {intent}",
                "data": None
            }

    except KeyError as e:
        return {
            "status": "error",
            "message": f"Missing parameter: {str(e)}",
            "data": None
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Internal error: {str(e)}",
            "data": None
        }
