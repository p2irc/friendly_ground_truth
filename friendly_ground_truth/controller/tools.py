"""
File Name: tools.py

Authors: Kyle Seidenthal

Date: 11-05-2020

Description: Definitions of tools that can be used in Friendly Ground Truth

"""


class FGTTool():
    """
    A class representing a tool that can be used on the image.

    Attributes:
        name: The name of the tool
        icon_string: A 64 bit encoded string representing an icon image
        id: A unique id for the tool
    """

    def __init__(self, name, icon_string, id):
        """
        Initialize the object

        Args:
            name: The name of the tool
            icon_string: A bytestring representing the icon for the tool
            id: A unique id for the tool
        """

        self._name = name
        self._icon_string = icon_string
        self._id = id

    @property
    def name(self):
        return self._name

    @property
    def icon_string(self):
        return self._icon_string

    @icon_string.setter
    def icon_string(self, string):
        self._icon_string = string

    @property
    def id(self):
        return self._id
