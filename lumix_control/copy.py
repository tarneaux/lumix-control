import argparse
import os
import re
import subprocess
import shutil

from . import size
from . import regex

def make_parser(copy_parser: argparse.ArgumentParser) -> None:
    copy_parser.add_argument("-d", "--destination", help="Destination folder", type=str, required=True, dest="destination", metavar="/path/to/destination")
    copy_parser.add_argument("-t", "--type", help="Types of files to download", type=str, required=True, dest="type", choices=["jpg", "mp4", "raw", "all", "image"])
    copy_parser.add_argument("-v", "--verbose", help="Verbose output", action="store_true", dest="verbose")
    # What do we do if the file already exists?
    copy_parser.add_argument("-o", "--overwrite", help="What to do if the file already exists", choices=["o", "s", "r"], default="r", dest="overwrite", metavar="{(o)verwrite,(s)kip,(r)ename}")
    copy_parser.add_argument("-c", "--convert", help="Convert the file to a different format", choices=["jpg", "png"], dest="convert", default=None, metavar="convert")



def main(args: argparse.Namespace) -> None:
    if args.convert is not None:
        # See if darktable-cli is installed
        if shutil.which("darktable-cli") is None:
            print("darktable-cli is not installed. Please install it to convert RAW files.")
            exit(1)
        if args.type not in ["raw", "all", "image"]:
            print("You can only convert RAW files. Please change --type to raw, image or all.")
            exit(1)
        print("WARNING: Converting the raw files to other formats will delete the original files.")

    if args.verbose:
        print("Listing devices...")
    fdisk_output = subprocess.check_output(["sudo", "fdisk", "-l"])
    fdisk_output = fdisk_output.decode("utf-8")
    if args.verbose:
        print("Found devices:")
        print(fdisk_output)

    if args.verbose:
        print("Finding device...")
    # Find the entry that has the right type: W95 FAT32 (LBA)
    # and extract the device name
    search = re.search(r"/dev/sd[a-z].*W95 FAT32 \(LBA\)", fdisk_output)
    if search is None:
        print("Could not find the camera. Make sure it's connected to the computer and that you have the right permissions.")
        return
    device = search.group(0).split(" ")[0]
    if args.verbose:
        print(f"Found device {device}")

    if args.verbose:
        print("Mounting device...")
    mount_point = "/tmp/lumix_control_mount"
    if not os.path.exists(mount_point):
        os.makedirs(mount_point)
    try:
        subprocess.check_call(["sudo", "mount", device, mount_point], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        if e.returncode == 32:
            if args.verbose:
                print("Device already mounted, unmounting...")
            subprocess.check_call(["sudo", "umount", device], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.check_call(["sudo", "mount", device, mount_point], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if args.verbose:
                print("Unmounted and mounted again.")
        else:
            raise e
    if args.verbose:
        print("Mounted device")

    DCIM_folder = os.path.join(mount_point, "DCIM")
    if args.verbose:
        print("Getting directory list...")
    dir_list = os.listdir(DCIM_folder)
    if args.verbose:
        print("Found directories:")
        print(dir_list)

    if args.verbose:
        print("Getting file list...")
    file_list = []
    for directory in dir_list:
        files_in_this_dir = os.listdir(os.path.join(DCIM_folder, directory))
        for file in files_in_this_dir:
            file_list.append(os.path.join(directory, file))
    if args.verbose:
        print(f"Found {len(file_list)} files")

    regexp = regex.file_type_regex(args.type)
    if args.verbose:
        print(f"Filtering files using regexp: {regexp}")
    filtered_file_list = []
    for file in file_list:
        if re.match(regexp, file.split("/")[-1]):
            filtered_file_list.append(file)
    if args.verbose:
        print(f"{len(filtered_file_list)} files left after filtering")

    if args.verbose:
        print("Comparing files...")
    files_to_copy = []
    for file in filtered_file_list:
        source, dest = os.path.join(DCIM_folder, file), os.path.join(args.destination, file.split("/")[-1])
        if not os.path.exists(dest):
            if (os.path.exists(dest.replace(".RW2", ".jpg")) and args.convert == "jpg") or (os.path.exists(dest.replace(".RW2", ".png")) and args.convert == "png"):
                if args.verbose:
                    print(f"Skipping {file} because the converted file already exists")
            else:
                files_to_copy.append((source, dest))
            continue
        if os.path.getsize(source) != os.path.getsize(dest) or os.path.getmtime(source) != os.path.getmtime(dest):
            if args.overwrite == "o":
                files_to_copy.append((source, dest))
            elif args.overwrite == "r":
                while True:
                    dest = dest.replace(".", "_copy.")
                    # Check if that file is the same as the source file
                    if os.path.getsize(source) == os.path.getsize(dest) and os.path.getmtime(source) == os.path.getmtime(dest):
                        break
                    if not os.path.exists(dest):
                        files_to_copy.append((source, dest))
                        break
            elif args.overwrite == "s":
                pass
            else:
                raise ValueError("Invalid value for overwrite")
    if args.verbose:
        print(f"{len(files_to_copy)} files left after comparing")

    total_size = sum([os.path.getsize(source) for source, _ in files_to_copy])
    
    # lowercase extensions in destinations
    files_to_copy = [
            (
                source,
                ".".join(dest.split(".")[:-1]) + "." + dest.split(".")[-1].lower()
            )
            for source, dest in files_to_copy
    ]

    LINE_CLEAR = '\x1b[2K' # <-- ANSI sequence

    if args.verbose:
        print("Copying files...")
    for i, (source, dest) in enumerate(files_to_copy):
        file_size = size.to_human(os.path.getsize(source))
        file_name = source.split("/")[-1]
        if args.verbose:
            print(f"Copying {source} to {dest} ({file_size})")
        else:
            print(LINE_CLEAR, end='\r')
            print(f"\rCopying {file_name} ({file_size}) ({i+1}/{len(files_to_copy)})", end="")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(source, dest)
        # Here we use .upper() because the regexps are in uppercase to match camera filenames, and we converted the extensions to lowercase
        if args.convert is not None and re.match(regex.file_type_regex("raw"), source.split("/")[-1].upper()):
            if args.verbose:
                print("Converting file...")
            else:
                print(LINE_CLEAR, end='\r')
                print(f"\rConverting {file_name} ({file_size}) ({i+1}/{len(files_to_copy)})", end="")
            # out: dest but with the extension changed to the one specified in the arguments
            out = ".".join(dest.split(".")[:-1]) + "." + args.convert
            subprocess.check_call(["darktable-cli", dest, out], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if args.verbose:
                print("Converted file")
            os.remove(dest) # Remove the original file

            
    if args.verbose:
        print("Done")
    else:
        print(LINE_CLEAR, end='\r')
        print(f"\rDone: copied {len(files_to_copy)} files ({size.to_human(total_size)})")
