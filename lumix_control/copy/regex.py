import re

def file_type_match(type: str, file: str) -> bool:
    types = {
            "raw" : ["raw", "rw2"],
            "jpg" : ["jpg"],
            "image" : ["jpg", "raw", "rw2"],
            "mp4" : ["mp4"],
            "all" : ["raw", "rw2", "jpg", "mp4"]
    } # rw2: Panasonic raw image (see https://en.wikipedia.org/wiki/Raw_image_format#Raw_filename_extensions_and_respective_camera_manufacturers_or_standard)
    file_regex = r".*" # match all files
    flags = re.IGNORECASE
    if type in types:
        # match all file types in the list
        file_regex += (
                r"\.(" + 
                r"|".join(types[type]) +
                r")"
        )
    return re.fullmatch(file_regex, file, flags=flags) is not None

