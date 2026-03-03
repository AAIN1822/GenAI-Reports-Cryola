def replace_paths(data, old_folder, new_folder):

    if isinstance(data, dict):
        return {
            key: replace_paths(value, old_folder, new_folder)
            for key, value in data.items()
        }

    elif isinstance(data, list):
        return [
            replace_paths(item, old_folder, new_folder)
            for item in data
        ]

    elif isinstance(data, str):
        return data.replace(old_folder, new_folder)

    return data