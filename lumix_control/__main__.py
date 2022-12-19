import argparse
from . import copy

parser = argparse.ArgumentParser(description="Lumix Control")
command = parser.add_subparsers(title="Command", dest="command")
command.required = True

copy_parser = command.add_parser("copy", help="Copy images from camera to computer")
copy.make_parser(copy_parser)


args = parser.parse_args()
if args.command == "copy":
    copy.main(args)

