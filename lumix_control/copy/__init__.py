import argparse
import subprocess
from ..copy.regex import file_type_match
import shutil
import os

def make_parser(copy_parser: argparse.ArgumentParser):
    conn_type = copy_parser.add_subparsers(title='connection type', dest='conn_type')

    wifi = conn_type.add_parser('wifi', help='Download files using wifi')
    usb = conn_type.add_parser('usb', help='Copy files using usb connection')

    # Arguments for both wifi and usb
    add_args = lambda *args, **kwargs: wifi.add_argument(*args, **kwargs) and usb.add_argument(*args, **kwargs)
    add_args('-v', '--verbose', action='store_true', help='Print verbose output')
    add_args("-o", "--output", help="Output directory", required=True, type=str)
    add_args("-e", "--extension", help="File extension to copy", choices=['jpg', 'raw', 'image', 'mp4', 'all'], default='all', type=str)
    add_args("-x", "--if-exists", help="What to do if file already exists", choices=['skip', 'overwrite', 'rename'], default='rename', type=str)

    # Arguments for wifi only
    wifi.add_argument('-i', '--ip', help='IP address of camera', type=str, metavar='IP', dest='ip', default="192.168.54.1")


def main(args):
    if args.conn_type == 'wifi':
        from ..copy.wifi import start_connection, list_files, colors, copy_file, get_file_size, get_file_mtime, end_connection, get_dest_name
    else:
        from ..copy.usb import start_connection, list_files, colors, copy_file, get_file_size, get_file_mtime, end_connection, get_dest_name

    colors.verbose = args.verbose
    debug = colors.debug

    debug('Starting connection')
    start_connection(args.ip if args.conn_type == 'wifi' else "")
    debug('Connection started')

    debug('Listing files on camera')
    files = list_files()
    debug(f'Found {len(files)} files')

    debug('Filtering files using regexp')
    files = filter_files(files, args, debug, get_file_size, get_file_mtime, get_dest_name)
    debug(f'Found {len(files)} files')
    
    debug('Copying files')
    total_size = 0
    for i, (file, output_file) in enumerate(files):
        file_size = get_file_size(file)
        total_size += file_size
        if not args.verbose:
            print("\33[2K\r", end='')
            print(f'\rCopying {output_file.split("/")[-1]} ({i}/{len(files)}) ({human_readable_size(file_size)}) ', end='')
        debug(f'Copying {file} to {output_file}')
        copy_file(file, output_file)
    if not args.verbose:
        print("\33[2K\r", end='')
        print(f'Copied {len(files)} files ({human_readable_size(total_size)})')
    debug('Finished copying files')
    end_connection()


def human_readable_size(size: int):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f'{size:.2f} {unit}'
        size //= 1024
    return f'{size:.2f} PB'


def filter_files(files: list, args: argparse.Namespace, debug, get_file_size, get_file_mtime, get_dest_name):
    debug(f'Filtering files by extension: {args.extension}')
    # Used to check if the file exists locally
    debug(f'Checking if output directory exists')
    if not os.path.isdir(args.output):
        debug(f'Output directory does not exist, creating it')
        os.makedirs(args.output)
    debug(f'Output directory exists')
    output = []
    for file in files:
        if not file_type_match(args.extension, file):
            debug(f'Skipping file {file} because it does not match extension {args.extension}')
            continue
        output_file = os.path.join(args.output, get_dest_name(file))
        if os.path.isfile(output_file) and os.path.getsize(output_file) == get_file_size(file) and (args.conn_type == 'wifi' or os.path.getmtime(output_file) == get_file_mtime(file)):
            debug(f'Skipping file {file} because it already exists locally (same size and modification time)')
            continue
        if os.path.isfile(output_file):
            # The file exists locally but it is different
            debug(f'File {file} exists locally but it is different')
            if args.if_exists == 'skip':
                debug(f'Skipping file {file} because it already exists locally')
                continue
            elif args.if_exists == 'rename':
                debug(f'Renaming file {file} because it already exists locally')
                output_file = rename_file(output_file, get_file_mtime(file), get_file_size(file))
                if output_file is None:
                    debug(f'{file} already exists locally as {output_file}, skipping')
                    continue
                debug(f'New file name: {output_file}')
            elif args.if_exists == 'overwrite':
                debug(f'Overwriting file {file}')
        output.append((file, output_file))
        debug(f'Adding file {file} to output list with output file {output_file}')
    return output


def rename_file(file: str, source_mtime: float, source_size: int):
    # Output format: file_1.ext
    file_name, file_ext = os.path.splitext(file)
    i = 1
    while os.path.isfile(file):
        # Prevent copying the same file twice: it could happen if the normal file and the renamed file have the same size and modification time
        if os.path.isfile(file) and os.path.getsize(file) == source_size and os.path.getmtime(file) == source_mtime:
            return None
        file = f'{file_name}_{i}{file_ext}'
        i += 1
    return file

