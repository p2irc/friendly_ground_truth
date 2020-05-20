"""
File Name: test_flood_add_tool.py

Authors: Kyle Seidenthal

Date: 13-05-2020

Description: Testing for the flood add tool.

"""

import pytest

from mock import MagicMock

from friendly_ground_truth.controller.tools import FloodAddTool


class TestFloodAddTool():
    """
    Tests for the Flood Add Tool
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

        tool = FloodAddTool(MagicMock())

        tool.tolerance = 7

        assert tool.tolerance == 7

        tool.tolerance = -5

        assert tool.tolerance == 7

        tool.tolerance -= 5

        assert tool.tolerance == 2

    def test_add_region(self, setup, mocker):
        """
        Test adding a region with the flood add tool.

        Args:
            setup: Setup for the tests.
            mocker: The mocker interface.

        Test Condition:
            The patch.flood_add() function is called with the given position
                and the current flood tool tolerance.
        """

        mock_patch = MagicMock()

        tool = FloodAddTool(MagicMock())
        tool.patch = mock_patch

        tool._add_region((6, 6))

        mock_patch.flood_add_region.assert_called_with((6, 6), tool.tolerance)
