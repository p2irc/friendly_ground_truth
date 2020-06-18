"""
File Name: test_controller.py

Authors: Kyle Seidenthal

Date: 19-05-2020

Description: Tests for the main controller.

"""

import pytest
import os

from friendly_ground_truth.controller.controller import Controller

from mock import MagicMock, PropertyMock


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
        mocker.patch('tkinter.IntVar')
        mocker.patch('PIL.ImageTk')
        mocker.patch('tkinter.PhotoImage')
        mocker.patch('tkinter.Toplevel')
        mocker.patch('tkinter.ttk')
        mocker.patch('tkinter.ttk.Style')
        mocker.patch('os.mkdir')
        mocker.patch('friendly_ground_truth.controller.controller.Controller'
                     '._ask_save_dir')

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

    def test_load_new_image_none_file(self, setup, dcp_mock,
                                      valid_rgb_image_path,
                                      controller, mocker):
        """
        Test loading a new image when the user cancels and no image path is
        returned.

        Args:
            setup: Setup for testing.
            dcp_mock: mock for the display_display_current_patch function.
            valid_rgb_image_path: A path to a valid RGB image.
            controller: The controller object to test with.
            mocker: The mocker interface.

        Test Condition:
            _image_path is none
            _image is none
            _display_current_patch is not called
        """
        mock_file = mocker.patch('tkinter.filedialog.askopenfilename')
        mock_file.return_value = None

        mocker.patch("friendly_ground_truth.view.main_window.MainWindow"
                     ".start_progressbar")
        mocker.patch("friendly_ground_truth.controller.controller.Controller."
                     "_update_progressbar")

        controller.load_new_image()

        assert controller._image_path is None
        assert controller._image is None
        assert not dcp_mock.called

    def test_load_new_image_not_found(self, setup, dcp_mock,
                                      valid_rgb_image_path,
                                      controller, mocker):
        """
        Test loading an image when a non-existant file is chosen.

        Args:
            setup: Setup for testing.
            dcp_mock: Mock for the display_current_patch function.
            valid_rgb_image_path: Path to a valid RGB image.
            controller: The controller to test with.
            mocker: Mocker interface.

        Test Condition:
            dcp_mock is not called.
        """
        mock_file = mocker.patch('tkinter.filedialog.askopenfilename')
        mock_file.return_value = valid_rgb_image_path

        def raise_FileException(x):
            raise FileNotFoundError

        mocker.patch("friendly_ground_truth.view.main_window"
                     ".MainWindow.start_progressbar",
                     side_effect=raise_FileException)

        mocker.patch("friendly_ground_truth.controller.controller.Controller."
                     "_update_progressbar")

        controller._main_window = MagicMock()
        controller._main_window.\
            start_progressbar.side_effect = raise_FileException

        controller.load_new_image()

        assert not dcp_mock.called

    def test_save_mask_none_image(self, setup, controller, mocker):
        """
        Test saving the mask when self._image is None.

        Args:
            setup: Setup for tests.
            controller: The controller to test.
            mocker: Mocker interface.

        Test Condition:
            _mask_saved is False
        """

        controller._image = None

        controller.save_mask()

        assert controller._mask_saved is False

    def test_save_mask_no_last_dir(self, setup, controller, mocker,
                                   valid_rgb_image_path):
        """
        Test saving the mask when there is no previous save directory.

        Args:
            setup: Setup for the tests.
            controller: The controller to test.
            mocker: Mocker interface.
            valid_rgb_image_path: A path to an RGB image.

        Test Condition:
            _last_save_dir is set to the directory returned by the dialog.
            _image.export_mask() is called.
        """

        mock_file = mocker.patch('tkinter.filedialog.askdirectory')
        mock_file.return_value = os.path.split(valid_rgb_image_path)[0]

        controller._image_path = valid_rgb_image_path
        controller._image = MagicMock()
        controller._previewed = True

        controller._last_save_dir = None

        controller.save_mask()

        assert controller._last_save_dir == mock_file.return_value
        controller._image.export_mask.assert_called()

    def test_save_mask_last_dir(self, setup, controller, mocker,
                                valid_rgb_image_path):
        """
        Test saving the mask when there is a previously selected save
        directory.

        Args:
            setup: Setup for the tests
            controller: The controller to test.
            mocker: The mocker interface
            valid_rgb_image_path: A path to a valid RGB image.

        Test Condition:
            _image.export_mask() is called
            _last_save_dir is set to the directory returned by the dialog.
        """

        mock_file = mocker.patch('tkinter.filedialog.askdirectory')
        mock_file.return_value = os.path.split(valid_rgb_image_path)[0]

        controller._image_path = valid_rgb_image_path
        controller._image = MagicMock()
        controller._previewed = True

        controller._last_save_dir = mock_file.return_value

        controller.save_mask()

        assert controller._last_save_dir == mock_file.return_value
        controller._image.export_mask.assert_called()

    def test_save_mask_none_dir(self, setup, controller, mocker):
        """
        Test saving the mask when the user does not select a directory.

        Args:
            setup: Setup for the tests.
            controller: The controller to test.
            mocker: The mocker interface.

        Test Condition:
            _image.export_mask() is not called.
        """
        mock_file = mocker.patch('tkinter.filedialog.askdirectory')
        mock_file.return_value = None

        controller._image = MagicMock()
        controller._previewed = True

        controller._last_save_dir = mock_file.return_value

        controller.save_mask()

        assert not controller._image.export_mask.called

    def test_save_mask_IOError(self, setup, controller, mocker,
                               valid_rgb_image_path):
        """
        Test saving the mask when exporting throws an IO Error

        Args:
            setup: Setup for the tests.
            controller: The controller to test.
            mocker: The mocker interface.

        Test Condition:
           _previewed is set to false
        """
        mock_file = mocker.patch('tkinter.filedialog.askdirectory')
        mock_file.return_value = valid_rgb_image_path

        def raise_IOException(x):
            raise IOError

        mock_image = MagicMock()
        mock_image.export_mask.side_effect = raise_IOException

        controller._image = mock_image

        controller._image_path = valid_rgb_image_path
        controller._previewed = True

        controller._last_save_dir = mock_file.return_value

        controller.save_mask()

        assert controller._previewed is False


class TestInteractions(TestController):
    """
    Tests for interaction functions like clicking.

    """

    def test_activate_tool_none_image(self, setup, controller):
        """
        Test activating a tool when there is not image loaded.

        Args:
            setup: Setup for the tests.
            controller: The controller for testing.

        Test Condition:
            The controller's current tool is not changed.
        """

        mock_tool = MagicMock()
        mock_tool.id.return_value = 0

        controller._current_tool = mock_tool

        controller._image = None

        old_tool = controller._current_tool

        controller.activate_tool(1)

        assert controller._current_tool.id == old_tool.id

    def test_activate_tool_not_persistant(self, setup, controller):
        """
        Test activating a non-persistant tool.

        Args:
            setup: Setup for tests.
            controller: The controller to test.

        Test Condition:
            The controller's current tool is not changed.
        """
        controller._image = MagicMock()

        mock_tool_1 = MagicMock()
        mock_tool_1.id = 0

        controller._current_tool = mock_tool_1

        mock_tool_2 = MagicMock()
        mock_tool_2.id = 1
        mock_tool_2.persistant = False

        old_tool = controller._current_tool

        tools = {0: mock_tool_1, 1: mock_tool_2}

        controller._image_tools = tools

        controller.activate_tool(1)

        assert controller._current_tool.id == old_tool.id

    def test_activate_tool_undo_not_empty(self, setup, controller):
        """
        Test activating the tool when the undo stack is empty.

        Args:
            setup: Setup for tests.
            controller: The controller to test.

        Test Condition:
            The main_window.enable_button function is called with the id of the
                undo button.
        """

        controller._image = MagicMock()

        mock_tool_1 = MagicMock()
        mock_tool_1.id = 0

        controller._current_tool = mock_tool_1

        mock_tool_2 = MagicMock()
        mock_tool_2.id = 1
        mock_tool_2.persistant = False

        tools = {0: mock_tool_1, 1: mock_tool_2}

        controller._image_tools = tools

        mock_undo = MagicMock()
        mock_undo.undo_empty = False

        controller._undo_manager = mock_undo

        controller.activate_tool(1)

        controller._main_window.enable_button\
            .assert_called_with(controller._undo_id)


    def test_adjust_tool(self, setup, controller):
        """
        Test adjusting the current tool.

        Args:
            setup: Setup for tests.
            controller: The controller to test with.

        Test Condition:
            The current tool's on_adjust() function is called with the given
                direction.
        """

        mock_tool = MagicMock()
        controller._current_tool = mock_tool

        direction = 1

        controller.adjust_tool(direction)

        mock_tool.on_adjust.assert_called_with(direction)

        direction = -1

        controller.adjust_tool(direction)

        mock_tool.on_adjust.assert_called_with(direction)

    def test_adjust_tool_undo_not_empty(self, setup, controller):
        """
        Test adjusting the current tool when the undo stack is not empty.

        Args:
            setup: Setup for tests.
            controller: The controller to test.

        Test Condition:
            The _main_window's enable_button function is called with the id of
                the undo button.
        """

        mock_tool = MagicMock()
        controller._current_tool = mock_tool

        direction = 1

        mock_undo = MagicMock()
        mock_undo.undo_empty = False

        controller._undo_manager = mock_undo

        controller.adjust_tool(direction)

        controller._main_window.enable_button\
            .assert_called_with(controller._undo_id)

    def test_click_event(self, setup, controller):
        """
        Test when a click event happens.

        Args:
            setup: Setup for tests.
            controller: The controller to test.

        Test Condition:
            The current tool's on_click is called.
        """

        mock_tool = MagicMock()

        controller._current_tool = mock_tool

        controller.click_event((5, 5))

        mock_tool.on_click.assert_called()

    def test_click_event_undo(self, setup, controller):
        """
        Test when a click event happens and the undo stack is not empty.

        Args:
            setup: Setup for tests.
            controller: The controller to test.

        Test Condition:
            _main_window.enable_button is called with the _undo_id
        """

        mock_undo = MagicMock()
        mock_undo.undo_empty = False

        controller._undo_manager = mock_undo

        controller.click_event((5, 5))

        controller._main_window.enable_button\
            .assert_called_with(controller._undo_id)

    def test_drag_event(self, setup, controller):
        """
        Test when a drag event occurs.

        Args:
            setup: Setup for tests.
            controller: The controller to test.

        Test Condition:
           The current tool's on_drag function is called.
        """

        mock_tool = MagicMock()

        controller._current_tool = mock_tool

        controller.drag_event((5, 5))

        mock_tool.on_drag.assert_called()

    def test_drag_undo(self, setup, controller):
        """
        Test a drag event when the undo stack is not empty.

        Args:
            setup: Setup for tests.
            controller: The controller for tests.

        Test Condition:
            _main_window.enable_button is called with the undo button's ID.
        """

        mock_undo = MagicMock()
        mock_undo.undo_empty = False

        mock_tool = MagicMock()

        controller._current_tool = mock_tool

        controller._undo_manager = mock_undo

        controller.drag_event((5, 5))

        controller._main_window.enable_button\
            .assert_called_with(controller._undo_id)

    def test_navigate_to_patch(self, setup, controller, mocker):
        """
        Test navigating to a patch.

        Args:
            setup: Setup for tests.
            controller: The controller to test.

        Test Condition:
            The controller's next_patch_callback is called.
        """

        controller._image = MagicMock()

        spy = mocker.spy(controller, '_next_patch_callback')

        controller.navigate_to_patch((5, 5))

        spy.assert_called()


class TestSettings(TestController):
    """
    Tests for functions that change the state of various settings.

    """

    def test_set_preferences(self, setup, controller, mocker):
        """
        Test setting the preferences given a dictionary of preferences.

        Args:
            setup: Setup for tests.
            controller: The controller to test.
            mocker: The mocker interface.

        Test Condition:
            _main_window.set_theme is called with the 'theme' property.
        """

        prefs = {"theme": "spaghetti"}

        controller.set_preferences(prefs)

        controller._main_window.set_theme.assert_called_with(prefs['theme'])

    def test_save_preferences(self, setup, controller, mocker):
        """
        Test saving the preferences of the user.

        Args:
            setup: Setup for tests.
            controller: The controller to test.
            mocker: The mocker interface.

        Test Condition:
            json.dump is called
        """

        mock_dump = mocker.patch('json.dump')

        controller.PREFERENCES_PATH = "./tests/data/user_preferences.json"

        controller.save_preferences({"theme": "Uncooked Pasta"})

        mock_dump.assert_called()
