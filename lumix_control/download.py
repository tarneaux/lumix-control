import argparse
import os
import re
import lumix_control


def make_parser(download_parser: argparse.ArgumentParser):
    download_parser.add_argument("-d", "--destination", help="Destination folder", type=str, required=True, dest="destination", metavar="/path/to/destination")
    download_parser.add_argument("-t", "--type", help="Types of files to download", type=str, required=True, dest="type", choices=["jpg", "mp4", "raw", "all", "image"])
    download_parser.add_argument("-v", "--verbose", help="Verbose output", action="store_true", dest="verbose")
    download_parser.add_argument("-i", "--ip", help="IP address of the camera", type=str, dest="ip", metavar="192.168.54.1", default="192.168.54.1")

def __make_regex(type: str):
    if type == "mp4":
        return r".*\.MP4"
    elif type == "jpg":
        return r".*\.JPG"
    elif type == "raw":
        return r".*\.RAW"
    elif type == "image":
        return r".*\.(JPG|RAW)"
    else:
        return r".*"

# Verify that there are still files to download
def __verify_remaining_urls(urls: list):
    if len(urls) == 0:
        print("No files to download.")
        exit(0)

def main(args: argparse.Namespace):
    if args.verbose:
        print(f"Downloading {args.type} files to {args.destination}")

    destination = os.path.expanduser(args.destination)
    if not os.path.exists(destination):
        print(f"Destination folder {destination} does not exist.")
        while True:
            answer = input("Do you want to create it? [Y/n] ")
            if answer.lower() == "y" or answer == "":
                os.makedirs(destination)
                break
            elif answer.lower() == "n":
                return
            else:
                print("Please answer with y or n.")
    
    regex = __make_regex(args.type)

    if args.verbose:
        print(f"Downloading files matching {regex} to {destination}")

    if args.verbose:
        print("Connecting to camera...")
    try:
        camera = lumix_control.CameraControl(args.ip)
    except Exception:
        print("Could not connect to camera. Verify that the IP address is correct and that you're connected to the camera by WiFi.")
        return
    if args.verbose:
        print("Connected.")

    if args.verbose:
        print("Getting file list...")
    # Filter out thumbnails using the DO prefix
    urls = [url for url in camera.get_picture_urls() if re.match("DO.*", url.split("/")[-1])]
    if args.verbose:
        print("Got file list.")
        print(f"Found {len(urls)} files.")

    __verify_remaining_urls(urls)

    if args.verbose:
        print("Comparing file list with regex...")
    urls = [url for url in urls if re.match(regex, url.split("/")[-1])]
    if args.verbose:
        print(f"{len(urls)} files remaining...")

    __verify_remaining_urls(urls)

    if args.verbose:
        print("Comparing sizes with local files if they exist...")
    urls = [url for url in urls if not (os.path.exists(os.path.join(destination, url.split("/")[-1])) and camera.get_remote_size(url) == os.path.getsize(os.path.join(destination, url.split("/")[-1])))]
    if args.verbose:
        print(f"{len(urls)} files remaining...")

    __verify_remaining_urls(urls)

    if args.verbose:
        print("Downloading files...")
    for i, url in enumerate(urls):
        if args.verbose:
            print(f"Downloading {url}...")
        else:
            image_name = url.split("/")[-1]
            print(f"\rDownloading {image_name}... ({i+1}/{len(urls)})", end="")
        camera.download_picture(url, destination)
        if args.verbose:
            print(f"Downloaded {url}.")
    if not args.verbose:
        print()


