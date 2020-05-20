"""
File Name: test_controller.py

Authors: Kyle Seidenthal

Date: 19-05-2020

Description: Tests for the main controller.

"""

import pytest
import os

from friendly_ground_truth.controller.controller import Controller

from mock import MagicMock


class TestController():
    """
    Base test class for the controller.
    """

    @pytest.fixture
    def setup(self, mocker):
        mocker.patch('friendly_ground_truth.view.main_window.MainWindow')
        mocker.patch('friendly_ground_truth.view.preview_window.PreviewWindow')
        mocker.patch('friendly_ground_truth.controller.tools.FGTTool')
        mocker.patch('friendly_ground_truth.controller.undo_manager')
        mocker.patch('friendly_ground_truth.model.model.Image')
        mocker.patch('tkinter.filedialog')
        mocker.patch('tkinter.messagebox')
        mocker.patch('PIL.ImageTk')
        mocker.patch('tkinter.PhotoImage')
        mocker.patch('tkinter.Toplevel')
    @pytest.fixture
    def dcp_mock(self, mocker):
        """
        Mock for the display_current_patch function, which can cause issues
        with testing if not mocked.

        Args:
            mocker: The mocker interface.
        """
        return mocker.patch("friendly_ground_truth.controller.controller."
                            "Controller._display_current_patch")

    @pytest.fixture
    def valid_rgb_image_path(self):
        return os.path.abspath('tests/data/KyleS22.jpg')

    @pytest.fixture
    def controller(self):
        controller = Controller(MagicMock())
        controller._main_window = MagicMock()
        return controller

class TestIo(TestController):
    """
    Tests for IO functions such as saving and loading images.

    """

    def test_load_new_image_no_load_dir(self, setup,
                                        dcp_mock, valid_rgb_image_path,
                                        controller,
                                        mocker):
        """
        Test loading a new image when there is no previous load directory.
        A valid file path is returned from the dialog.

        Args:
            setup: Setup for the tests.
            mocker: Mocker interface.

        Test Condition:
            _last_load_dir is set to the returned directory
            _image_path is set to the returned file
            _image is set to an Image object
            _display_current_patch is called
        """

        mock_file = mocker.patch('tkinter.filedialog.askopenfilename')
        mock_file.return_value = valid_rgb_image_path

        mocker.patch("friendly_ground_truth.view.main_window.MainWindow"
                     ".start_progressbar")
        mocker.patch("friendly_ground_truth.controller.controller.Controller."
                     "_update_progressbar")

        file_dir = os.path.split(valid_rgb_image_path)[0]

        controller.load_new_image()

        assert controller._last_load_dir == file_dir
        assert controller._image_path == valid_rgb_image_path
        assert controller._image is not None
        dcp_mock.assert_called()




class TestInteractions(TestController):
    """
    Tests for interaction functions like clicking.

    """
