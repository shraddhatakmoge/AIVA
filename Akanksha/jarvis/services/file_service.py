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
    Finds the REAL Desktop or Documents folder, even if OneDrive is active.
    """
    # 1. Start with the standard User Profile
    user_profile = os.path.expanduser("~")
    
    # 2. Check for OneDrive Desktop/Documents first
    onedrive_path = os.path.join(user_profile, "OneDrive")
    
    # Default search order: OneDrive -> Local User Folder
    if os.path.exists(onedrive_path):
        base_dir = onedrive_path
    else:
        base_dir = user_profile

    # 3. If the user gave an absolute path, use it. 
    # Otherwise, default to the Desktop so we can see the results!
    if not os.path.isabs(path):
        target_dir = os.path.join(base_dir, "Desktop")
        return os.path.join(target_dir, path)

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
