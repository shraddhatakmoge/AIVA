import os
import shutil


def create_file(path, content=""):
    try:
        with open(path, "w") as f:
            f.write(content)

        return {
            "status": "success",
            "message": f"File created at {path}",
            "data": None
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "data": None
        }


def delete_file(path):
    try:
        os.remove(path)

        return {
            "status": "success",
            "message": f"File deleted from {path}",
            "data": None
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "data": None
        }


def rename_file(old_path, new_path):
    try:
        os.rename(old_path, new_path)

        return {
            "status": "success",
            "message": f"File renamed to {new_path}",
            "data": None
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "data": None
        }


def move_file(source, destination):
    try:
        shutil.move(source, destination)

        return {
            "status": "success",
            "message": f"File moved to {destination}",
            "data": None
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "data": None
        }


def copy_file(source, destination):
    try:
        shutil.copy(source, destination)

        return {
            "status": "success",
            "message": f"File copied to {destination}",
            "data": None
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "data": None
        }


def read_file(path):
    try:
        with open(path, "r") as f:
            content = f.read()

        return {
            "status": "success",
            "message": "File read successfully",
            "data": content
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "data": None
        }
