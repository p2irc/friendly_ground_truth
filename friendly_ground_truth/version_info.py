"""
File Name: version_info.py

Authors: Kyle Seidenthal

Date: 03-03-2020

Description: Version Info

"""
import sys
import re
import requests

REPO_URL = "https://api.github.com/repos/KyleS22/friendly_ground_truth/" + \
           "releases/latest"


class VersionInfo():

    def __init__(self):
        self.VERSION_MAJOR = 0
        self.VERSION_MINOR = 7
        self.VERSION_PATCH = 1

    def get_version_string(self):
        return "v" + str(self.VERSION_MAJOR) + '.' +\
                str(self.VERSION_MINOR) + '.' +\
                str(self.VERSION_PATCH)

    def check_newer_version(self, version_string):
        version_string = version_string.strip('v')
        parts = version_string.split(".")
        v_maj = int(parts[0])
        v_min = int(parts[1])
        v_patch = int(parts[2])

        if v_maj > self.VERSION_MAJOR:
            return True

        elif v_maj == self.VERSION_MAJOR:

            if v_min > self.VERSION_MINOR:
                return True

            elif v_min == self.VERSION_MINOR:

                if v_patch > self.VERSION_PATCH:
                    return True

        return False

    def get_newest_release_info(self):

        response = requests.get(REPO_URL)
        version = response.json()["name"]
        version = version[version.index('v'):]

        return version

    def check_for_update(self):

        latest = self.get_newest_release_info()

        if self.check_newer_version(latest):
            return "There is a new version, " + latest + "."
        else:
            return "There are no updates."


def main(args):

    if len(args) < 2:
        print("Need to specify a version string: x.y.z")
        sys.exit(1)

    version_string = args[1]

    version_string = version_string.strip("v")

    version_pattern = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")

    if not version_pattern.match(version_string):
        print("Invalid version string.  Must be in format: x.y.z")

        sys.exit(1)

    version_info = VersionInfo()

    if version_info.check_newer_version(version_string):
        print("Installing Update")
        sys.exit(0)
    else:
        print("Already up to date")
        sys.exit(2)


if __name__ == "__main__":
    main(sys.argv)
