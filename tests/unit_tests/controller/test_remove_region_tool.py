"""
File Name: test_add_region_tool.py

Authors: Kyle Seidenthal

Date: 13-05-2020

Description: Tests for the AddRegion Tool

"""
import pytest

from mock import MagicMock

from friendly_ground_truth.controller.tools import RemoveRegionTool


class TestRemoveRegionTool():
    """
    Tests for the Remove Region Tool
    """

    @pytest.fixture
    def setup(self, mocker):
        mocker.patch("friendly_ground_truth.model.model.Patch")

    def test_set_brush_radius(self, setup):
        """
        Test setting the brush radius.

        Args:
            setup: Setup for mocking patches

        Test Condition:
            The brush radius can be set to any positive number.
        """
        tool = RemoveRegionTool()

        tool.brush_radius = 36

        assert tool.brush_radius == 36

        tool.brush_radius -= 10

        assert tool.brush_radius == 26

        tool.brush_radius = 0

        assert tool.brush_radius == 0

        tool.brush_radius = -1

        assert tool.brush_radius == 0

        tool.brush_radius -= 6

        assert tool.brush_radius == 0

        tool.brush_radius = 1

        tool.brush_radius -= 10

        assert tool.brush_radius == 1

    def test_draw(self, setup, mocker):
        """
        Test drawing a circle at a given position.

        Args:
            setup: Setup for the patch mock.
            mocker: The mocker interface.

        Test Condition:
            The patch's add_region function is called.
        """

        mock_patch = MagicMock()

        tool = RemoveRegionTool()
        tool.patch = mock_patch

        tool.draw((10, 10))

        mock_patch.remove_region.assert_called()
