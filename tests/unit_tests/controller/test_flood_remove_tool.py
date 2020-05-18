"""
File Name: test_flood_remove_tool.py

Authors: Kyle Seidenthal

Date: 13-05-2020

Description: Testing for the flood remove tool.

"""

import pytest

from mock import MagicMock

from friendly_ground_truth.controller.tools import FloodRemoveTool


class TestFloodRemoveTool():
    """
    Tests for the Flood Remove Tool
    """

    @pytest.fixture
    def setup(self, mocker):
        mocker.patch("friendly_ground_truth.model.model.Patch")

    def test_set_tolerance(self, setup):
        """
        Test setting the tolerance to various values.

        Args:
            setup: Setup for the tests.

        Test Condition:
            Setting to a positive value should pass.
            Setting to a negatve value should fail.
        """

        tool = FloodRemoveTool()

        tool.tolerance = 7

        assert tool.tolerance == 7

        tool.tolerance = -5

        assert tool.tolerance == 7

        tool.tolerance -= 5

        assert tool.tolerance == 2

    def test_remove_region(self, setup, mocker):
        """
        Test removeing a region with the flood remove tool.

        Args:
            setup: Setup for the tests.
            mocker: The mocker interface.

        Test Condition:
            The patch.flood_remove() function is called with the given position
                and the current flood tool tolerance.
        """

        mock_patch = MagicMock()

        tool = FloodRemoveTool()
        tool.patch = mock_patch

        tool.remove_region((6, 6))

        mock_patch.flood_remove.assert_called_with((6, 6), tool.tolerance)
