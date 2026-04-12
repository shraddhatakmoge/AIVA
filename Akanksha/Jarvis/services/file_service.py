import os

from .file_operations import (
    create_file,
    delete_file,
    rename_file,
    move_file,
    copy_file,
    read_file,
    open_item
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
    Strictly forces the REAL local Desktop folder.
    Also features 'Smart Extension' detection for missing file types.
    """
    user_profile = os.path.expanduser("~")
    base_dir = os.path.join(user_profile, "Desktop")

    # Build the target path
    if not os.path.isabs(path):
        target_path = os.path.join(base_dir, path)
    else:
        target_path = path

    # 🔥 THE SMART EXTENSION FIX
    # If the exact file doesn't exist, intelligently check for common extensions
    if not os.path.exists(target_path):
        if os.path.exists(target_path + ".txt"):
            return target_path + ".txt"
        elif os.path.exists(target_path + ".docx"):
            return target_path + ".docx"

    return target_path

def handle_file_command(intent, entities):
    try:
        # 🔥 SMART FILE CREATION
        if intent == "create_file":
            filename = entities["path"]
            
            # Default to .txt if no extension was spoken
            if "." not in filename:
                filename += ".txt"
                
            path = resolve_path(filename)
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
        
        elif intent == "open_item":
            path = resolve_path(entities["path"])
            return open_item(path)

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
