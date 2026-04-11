import os
import shutil


def create_folder(path):
    try:
        # exist_ok=True prevents errors if the folder is already there
        os.makedirs(path, exist_ok=True) 
        return {
            "status": "success",
            "message": f"Folder created successfully at {path}"
        }
    except PermissionError:
        return {"status": "error", "message": "Permission denied. Try running as Admin."}
    except Exception as e:
        return {"status": "error", "message": f"System error: {str(e)}"}

def delete_folder(path):
    try:
        shutil.rmtree(path)

        return {
            "status": "success",
            "message": f"Folder deleted from {path}",
            "data": None
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "data": None
        }


def rename_folder(old_path, new_path):
    try:
        os.rename(old_path, new_path)

        return {
            "status": "success",
            "message": f"Folder renamed to {new_path}",
            "data": None
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "data": None
        }
