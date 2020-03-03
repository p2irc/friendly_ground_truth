"""
File Name: version_info.py

Authors: Kyle Seidenthal

Date: 03-03-2020

Description: Version Info

"""
import sys
import re


class VersionInfo():

    def __init__(self):
        self.VERSION_MAJOR = 0
        self.VERSION_MINOR = 0
        self.VERSION_PATCH = 0

    def get_version_string(self):
        return "v" + str(self.VERSION_MAJOR) + str(self.VERSION_MINOR) +\
                self.VERSION_PATCH

    def check_newer_version(self, version_string):

        parts = version_string.split(".")
        print(parts)
        v_maj = int(parts[0])
        v_min = int(parts[1])
        v_patch = int(parts[2])

        if v_maj > self.VERSION_MAJOR:
            return True

        if v_maj == self.VERSION_MAJOR:

            if v_min > self.VERSION_MINOR:
                return True

            if v_min == self.VERSION_MINOR:

                if v_patch > self.VERSION_PATCH:
                    return True


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Need to specify a version string: x.x.x")
        sys.exit(1)

    version_string = sys.argv[1]

    version_string = version_string.strip("v")

    version_pattern = re.compile("[0-9]+\.[0-9]+\.[0-9]+")

    if not version_pattern.match(version_string):
        print("Invalid version string.  Must be in format: x.x.x")
        sys.exit(1)

    version_info = VersionInfo()

    if version_info.check_newer_version(version_string):
        print("Installing Update")
        sys.exit(0)
    else:
        print("Already up to date")
        sys.exit(2)
