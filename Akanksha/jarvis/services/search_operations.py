import os


def search_by_name(directory, filename):
    results = []
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if filename.lower() in file.lower():
                    results.append(os.path.join(root, file))

        return {
            "status": "success",
            "message": "Search completed",
            "data": results
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "data": None
        }


def search_by_extension(directory, extension):
    results = []
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(extension):
                    results.append(os.path.join(root, file))

        return {
            "status": "success",
            "message": "Extension search completed",
            "data": results
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "data": None
        }
