"""
File Name: test_FGTTool.py

Authors: Kyle Seidenthal

Date: 11-05-2020

Description: Tests for the FGT Tool Class

"""
import pytest

from friendly_ground_truth.controller.tools import FGTTool

from mock import MagicMock


class TestFGTTool():
    """
    Tests for the FGTTool superclass

    """

    def test_init(self):
        """
        Test creating a new tool


        Test Condition:
            The name, icon_string, and ids are all set
        """
        tool = FGTTool("test tool", 'abc', 123, MagicMock(), MagicMock())

        assert tool.name == "test tool"
        assert tool.icon_string == 'abc'
        assert tool.id == 123

    def test_set_icon_string(self):
        """
        Test setting the icon string

        Test Condition:
            The icon string is replaced with a new string
        """

        tool = FGTTool("test tool", 'abc', 123, MagicMock(), MagicMock())

        tool.icon_string = 'xyz'

        assert tool.icon_string == 'xyz'

    def test_set_cursor(self):
        """
        Test setting the cursor.


        Test Condition:
            The cursor is set.
        """

        tool = FGTTool("test tool", 'abc', 123, MagicMock(), MagicMock(),
                       cursor='hand')

        assert tool.cursor == 'hand'
