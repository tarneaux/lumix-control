import shutil
from .. import colors
debug = colors.debug
error = colors.error
info = colors.info

import subprocess
import os

GX80_UUID = "9016-4EF8"
GX80_PATH = "/dev/disk/by-uuid/" + GX80_UUID
GX80_MOUNTPOINT = "/tmp/gx80"
GX80_DCIM_PATH = GX80_MOUNTPOINT + "/DCIM"

def check_connected():
    debug("Checking if the camera is connected")
    if not os.path.exists(GX80_PATH):
        error("Camera not connected: " + GX80_PATH + " does not exist.")
        error("Please check that your GX80 Camera is connected to your computer by usb.")
        exit(1)



def mount():
    debug(f"Creating mountpoint at {GX80_MOUNTPOINT} if it does not exist")
    if not os.path.exists(GX80_MOUNTPOINT):
        os.mkdir(GX80_MOUNTPOINT)
    debug("Unmounting the camera if it is already mounted")
    subprocess.run(["sudo", "umount", GX80_MOUNTPOINT], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    debug("Mounting the camera")
    try:
        subprocess.check_call(["sudo", "mount", GX80_PATH, GX80_MOUNTPOINT], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        error("Failed to mount the camera")
        if e.returncode == 32:
            error("The camera is already mounted elsewhere. Please unmount it first.")
            info("You can use the following command to unmount it:")
            info("sudo umount " + GX80_PATH)
        exit(1)


def list_files():
    def recursive_list_files(path):
        files = []
        for f in os.listdir(path):
            if os.path.isdir(os.path.join(path, f)):
                files.extend(recursive_list_files(os.path.join(path, f)))
            else:
                files.append(os.path.join(path, f))
        return files
    try:
        files = recursive_list_files(GX80_DCIM_PATH)
    except FileNotFoundError as e:
        error("Failed to list files on the camera")
        raise e
    return files


def start_connection(_): # argument used by wifi version
    check_connected()
    mount()

def end_connection():
    debug("Unmounting the camera")
    subprocess.run(["sudo", "umount", GX80_MOUNTPOINT], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    debug("Removing mountpoint")
    os.rmdir(GX80_MOUNTPOINT)

def copy_file(file, destination):
    debug(f"Copying {file} to {destination}")
    shutil.copy2(file, destination)

def get_file_size(file: str) -> int:
    return os.path.getsize(file)

def get_file_mtime(file: str) -> float:
    return os.path.getmtime(file)

def get_dest_name(file: str) -> str:
    return os.path.basename(file)
