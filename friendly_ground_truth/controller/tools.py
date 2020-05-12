"""
File Name: tools.py

Authors: Kyle Seidenthal

Date: 11-05-2020

Description: Definitions of tools that can be used in Friendly Ground Truth

"""
import logging

from friendly_ground_truth.view.icons.icon_strings import (threshold_icon)

module_logger = logging.getLogger('friendly_gt.controller.tools')


class FGTTool():
    """
    A class representing a tool that can be used on the image.

    Attributes:
        name: The name of the tool
        icon_string: A 64 bit encoded string representing an icon image
        id: A unique id for the tool
    """

    def __init__(self, name, icon_string, id, cursor='none'):
        """
        Initialize the object

        Args:
            name: The name of the tool
            icon_string: A bytestring representing the icon for the tool
            id: A unique id for the tool
            cursor: The default cursor for this tool.  Default value is 'none'
        """
        self._logger = logging\
            .getLogger('friendly_gt.controller.tools.FGTTool')

        self._name = name
        self._icon_string = icon_string
        self._id = id
        self._cursor = cursor

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

    @property
    def cursor(self):
        return self._cursor


class ThresholdTool(FGTTool):
    """
    Tool representing a threshold action.

    Attributes:
        threshold: The value of the threshold. Between 0 and 1.
        increment: The amount to change the threshold by when adjusting
        patch: The current patch to operate on
    """

    def __init__(self):

        super(ThresholdTool, self)\
            .__init__("Threshold Tool", threshold_icon, 1, 'arrow')

        self._logger = logging\
            .getLogger('friendly_gt.controller.tools.ThresholdTool')

        self._threshold = 0
        self._increment = 0.01
        self._patch = None

    @property
    def threshold(self):
        return self._threshold

    @threshold.setter
    def threshold(self, value):
        if value <= 1 and value >= 0:
            self._threshold = value
            self._patch.threshold = value

    @property
    def increment(self):
        return self._increment

    @increment.setter
    def increment(self, value):
        self._increment = value

    @property
    def patch(self):
        return self._patch

    @patch.setter
    def patch(self, patch):
        self._patch = patch
        self._threshold = patch.threshold

    def adjust_threshold(self, direction):
        """
        Adjust the current threshold

        Args:
            direction: An integer, positive indicates increasing threshold,
                       negative idicates decreasing threshold

        Returns:
            None, the patch threshold will be set accordingly
        """

        if direction > 0:
            self.threshold += self.increment
        else:
            self.threshold -= self.increment
