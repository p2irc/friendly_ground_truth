"""
File Name: embed_icon.py

Authors: Kyle Seidenthal

Date: 23-04-2020

Description: Script to embed icon png images

"""
import sys
import base64

MAX_LINE_LENGTH = 79

def get_string_encoding(image_path):
    """
    Get the base64 encoding string of the given image

    :param image_path: The path to the image
    :returns: The base64 byte string of the image
    """

    with open(image_path, 'rb') as image:
        string = base64.b64encode(image.read())

    s = ''

    L = [string[i:i+1] for i in range(len(string))]

    for i in range(len(L)):
        s += L[i].decode()

    return s

def append_string_to_icon_file(icon_name, icon_string, icon_file):
    """
    Append the icon string as a variable in the icon file

    :param icon_name: A valid python variable name for the icon
    :param icon_string: The encoded icon string
    :param icon_file: The path to the icon file
    :returns: None
    """

    output = "\n\n" + icon_name + " = ("
    spaces = len(output) - 2

    output += "b\""
    length = len(output)

    for c in icon_string:

        if length >= MAX_LINE_LENGTH-1:
            output += "\"\n"
            for i in range(spaces):
                output += " "

            length = 0
            output += "b\""
            length += 2 + spaces

        output += c
        length += 1

    if length >= MAX_LINE_LENGTH-1:
        output += "\"\n"
        for i in range(spaces):
            output += " "

        length = 0
        output += ")\n"

    else:
        output += "\")\n"


    with open(icon_file, 'a') as f:
        f.write(output)

def main(icon_path, icon_name, string_file):

    string = get_string_encoding(icon_path)

    append_string_to_icon_file(icon_name, string, string_file)

if __name__ == "__main__":

    if len(sys.argv) < 4:
        print("Usage: python embed_icon.py path_to_icon icon_name"
              "path_to_icon_string_file")

    icon_path = sys.argv[1]
    icon_name = sys.argv[2]
    string_file = sys.argv[3]

    main(icon_path, icon_name, string_file)
