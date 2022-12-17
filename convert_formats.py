# This does not use the library, it is just a way to convert the raw files to pngs

import os
import re


def convert_to_png(input_file, output_file):
    # use darktable-cli to convert the raw file to a png
    os.system("darktable-cli " + input_file + " " + output_file)


def convert_all_files(input_folder, output_folder):
    # get all the files in the input folder
    files = os.listdir(input_folder)

    # loop through all the files
    for file in files:
        # get the file name without the extension
        file_name = os.path.splitext(file)[0]

        # check if the file is a raw file
        if re.search(".*\\.RAW", file):
            # convert the file to a png
            convert_to_png(os.path.join(input_folder + file), os.path.join(output_folder + file_name + ".png"))

if __name__ == "__main__":
    input_folder = os.path.join(os.getenv("HOME"), "Pictures/pana/raw/")
    output_folder = os.path.join(os.getenv("HOME"), "Pictures/pana/png/")

    # convert all the files
    convert_all_files(input_folder, output_folder)
    
