from .. import colors

debug = colors.debug
error = colors.error

from .. import lumix_control

def start_connection(ip: str):
    global camera
    debug(f"Connecting to camera at {ip}")
    try:
        camera = lumix_control.CameraControl(ip)
    except Exception:
        error(f"Error connecting to camera. Verify that the IP address is correct and that you are connected to the camera's access point.")
        exit(1)


def list_files():
    files = [
            file
            for file in camera.get_picture_urls()
            if file.split("/")[-1].startswith("DO") # Filter out thumbnails
            ]
    return files

def copy_file(url: str, path: str):
    camera.download_picture(url, path)

def get_dest_name(url: str):
    return url.split("/")[-1].replace("DO", "P").replace(".RAW", ".RW2")

def get_file_size(url: str):
    return camera.get_remote_size(url)

def get_file_mtime(*args, **kwargs):
    return None


def end_connection():
    camera.close()
