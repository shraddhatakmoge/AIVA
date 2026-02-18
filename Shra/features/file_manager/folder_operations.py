import os
import shutil


def create_folder(path):
    try:
        os.makedirs(path, exist_ok=True)

        return {
            "status": "success",
            "message": f"Folder created at {path}",
            "data": None
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "data": None
        }


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
