def file_type_regex(type: str):
    if type == "mp4":
        return r".*\.MP4"
    elif type == "jpg":
        return r".*\.JPG"
    elif type == "raw":
        return r".*\.(RAW|RW2)"
    elif type == "image":
        return r".*\.(JPG|RAW|RW2)"
    else:
        return r".*"

