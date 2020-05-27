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
        mocker.patch('tkinter.ttk')
        mocker.patch('tkinter.ttk.Style')
        mocker.patch('os.mkdir')

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

    def test_create_prefs_path_windows(self, setup, mocker):
        """
        Test creating the preferences path if the platform is windows.

        Args:
            setup: Setup for the controller.
            mocker: Mocker interface.

        Test Condition:
            The PREFERENCES_PATH variable is
                './user_preferences.json'
        """

        from friendly_ground_truth.controller import controller as ct
        ct.platform = 'win32'

        controller = Controller(MagicMock())

        assert controller.PREFERENCES_PATH == './user_preferences.json'

    def test_create_prefs_path_unix(self, setup, mocker):
        """
        Test creating the preferences path if the platform is unix based.

        Args:
            setup: Setup for the controller.
            mocker: Mocker interface.

        Test Condition:
            The PREFERENCES_PATH variable is
                '/home/$USER/user_preferences.json'
        """

        from friendly_ground_truth.controller import controller as ct
        ct.platform = 'Linux'

        fakehome = "./tests/data/fakehome/"

        mocker.patch('friendly_ground_truth.controller.'
                     'controller.Controller.load_preferences',
                     return_value={'theme': 'Light'})

        mocker.patch('os.path.expanduser',
                     return_value=fakehome)

        mocker.patch('os.path.exists', return_value=True)

        controller = Controller(MagicMock())

        assert controller.PREFERENCES_PATH == os.\
            path.join(fakehome, '.friendly_ground_truth/user_preferences.json')

        mocker.patch('friendly_ground_truth.controller.'
                     'controller.Controller.load_preferences',
                     return_value={'theme': 'Dark'})

        mocker.patch('os.path.exists', return_value=False)
        controller = Controller(MagicMock())

        assert controller.PREFERENCES_PATH == os.\
            path.join(fakehome, '.friendly_ground_truth/user_preferences.json')


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

    def test_load_new_image_with_load_dir(self, setup, dcp_mock,
                                          valid_rgb_image_path,
                                          controller, mocker):
        """
        Test loading a new image when there is a previous load directory.
        A valid file path is returned from the dialog.

        Args:
            setup: Setup for the tests.
            dcp_mock: Mock for the display current patch function.
            valid_rgb_image_path: A path to a valid rgb image.
            controller: The controller to use.
            mocker: Mocker interface.

        Test Condition:
            _last_load_dir is set to the returned directory.
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
        controller._last_load_dir = file_dir

        controller.load_new_image()

        assert controller._last_load_dir == file_dir
        assert controller._image_path == valid_rgb_image_path
        assert controller._image is not None
        dcp_mock.assert_called()


class TestInteractions(TestController):
    """
    Tests for interaction functions like clicking.

    """
