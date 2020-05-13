"""
File Name: test_no_root_tool.py

Authors: Kyle Seidenthal

Date: 13-05-2020

Description: Tests for the No Root Tool

"""

import pytest

from mock import MagicMock

from friendly_ground_truth.controller.tools import NoRootTool


class TestNoRootTool():
    """
    Tests for the No Root Tool
    """

    @pytest.fixture
    def setup(self, mocker):
        mocker.patch("friendly_ground_truth.model.model.Patch")

    def test_no_root(self, setup, mocker):
        """
        Test activating the No Root Tool.

        Args:
            setup: Setup for mocking.
            mocker: The mocker interface.

        Test Condition:
            The patch.clear_mask() function is called.
        """
        mock_patch = MagicMock()

        tool = NoRootTool()
        tool.patch = mock_patch

        tool.no_root()

        mock_patch.clear_mask.assert_called()
