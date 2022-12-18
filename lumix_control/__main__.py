import argparse
from . import download

def main():
    parser = argparse.ArgumentParser(description="Lumix Control")
    command = parser.add_subparsers(title="Command", dest="command")
    command.required = True
    download_parser = command.add_parser("download", help="Download images from camera")
    download.make_parser(download_parser)
    convert = command.add_parser("convert", help="Convert images to other formats")
    args = parser.parse_args()
    if args.command == "download":
        download.main(args)
    elif args.command == "convert":
        print("Not implemented yet, sorry")

if __name__ == "__main__":
    main()
