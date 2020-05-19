"""
File Name: test_threshold_tool.py

Authors: Kyle Seidenthal

Date: 12-05-2020

Description: Tests for the Threshold tool.

"""

import pytest

from mock import MagicMock

from friendly_ground_truth.controller.tools import ThresholdTool


class TestThresholdTool():
    """
    Tests for the Threshold Tool
    """

    @pytest.fixture
    def setup(self, setup, mocker):
        mocker.patch("friendly_ground_truth.model.model.Patch")

    def test_set_threshold_valid(self, mocker):
        """
        Test setting the threshold with a valid value

        Args:
            mocker: The mocker interface

        Test Condition:
            The threshold property has the correct value
            The threshold value for the patch is set to the same value
        """

        thresh_tool = ThresholdTool(MagicMock())

        mock_patch = MagicMock()
        mock_patch.threshold = -1

        thresh_tool.patch = mock_patch
        thresh_tool._new_patch = False
        thresh_tool.threshold = 0.5

        assert thresh_tool.threshold == 0.5
        assert thresh_tool.patch.threshold == 0.5

        thresh_tool.threshold += 0.1

        assert thresh_tool.threshold == 0.6
        assert thresh_tool.patch.threshold == 0.6

    def test_set_threshold_invalid(self, mocker):
        """
        Test setting the threshold with an invalid value.

        Args:
            mocker: The mocker interface

        Test Condition:
            The threshold property is still 0
            The patch threshold is still 0
        """

        thresh_tool = ThresholdTool(MagicMock())

        patch_mock = MagicMock()
        patch_mock.threshold = 0

        thresh_tool._patch = patch_mock

        thresh_tool.threshold = 7

        assert thresh_tool.threshold == 0
        assert thresh_tool.patch.threshold == 0

        thresh_tool.threshold += 7

        assert thresh_tool.threshold == 0
        assert thresh_tool.patch.threshold == 0

    def test_set_increment(self):
        """
        Test setting the increment.


        Test Condition:
            The increment is set.
        """

        thresh_tool = ThresholdTool(MagicMock())

        thresh_tool.increment = 76

        assert thresh_tool.increment == 76

    def test_set_patch(self):
        """
        Test setting the patch.


        Test Condition:
            The patch is set to the given patch
            The threshold is set to the patches threshold
        """

        thresh_tool = ThresholdTool(MagicMock())

        mock_patch = MagicMock()
        mock_patch.threshold = 0.5

        thresh_tool.patch = mock_patch

        assert thresh_tool._patch == mock_patch
        assert thresh_tool.threshold == 0.5

    def test_adjust_threshold_up(self):
        """
        Test increasing the threshold value.


        Test Condition:
            The threshold is decremented by the increment value.
        """

        thresh_tool = ThresholdTool(MagicMock())
        thresh_tool._patch = MagicMock()
        thresh_tool._patch.mock_patch.threshold.return_value = 0.5

        thresh_tool.threshold = 0.5

        old_thresh = thresh_tool.threshold

        thresh_tool._adjust_threshold(1)

        assert thresh_tool.threshold == (old_thresh - thresh_tool.increment)

    def test_adjust_threshold_down(self):
        """
        Test decreasing the threshold value.


        Test Condition:
            The threshold is incremented by the increment value.
        """

        thresh_tool = ThresholdTool(MagicMock())
        thresh_tool._patch = MagicMock()
        thresh_tool._patch.mock_patch.threshold.return_value = 0.5

        thresh_tool.threshold = 0.3

        old_thresh = thresh_tool.threshold

        thresh_tool._adjust_threshold(-1)

        assert thresh_tool.threshold == (old_thresh + thresh_tool.increment)
