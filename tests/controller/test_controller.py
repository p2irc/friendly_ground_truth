"""
File Name: test_controller.py

Authors: Kyle Seidenthal

Date: 09-03-2020

Description: Test cases for the controller moduel

"""

import pytest
import os
import mock
import tkinter.filedialog
import numpy as np

from mock import MagicMock, PropertyMock

from friendly_ground_truth.controller.controller import Controller, Mode
from friendly_ground_truth.view.tk_view import MainWindow
from friendly_ground_truth.model.model import Patch, Image

from skimage import io
from skimage.color import rgb2gray


class TestController:
    """
    Tests pertaining to the controller class
    """

    @pytest.fixture
    def valid_rgb_image_path(self):
        return os.path.abspath('tests/data/KyleS22.jpg')

    @pytest.fixture
    def valid_grayscale_image_path(self):
        return os.path.abspath('tests/data/KyleS22_gray.png')

    @pytest.fixture
    def invalid_image_path(self):
        return 'invalid/image/path'

    @pytest.fixture
    def directory_path(self):
        return os.path.abspath('tests/data/')

    @pytest.fixture
    def test_image_data(self):
        return rgb2gray(io.imread(os.path.abspath('tests/data/KyleS22.jpg')))

    @pytest.fixture
    def setup(self, mocker):

        self.mock_MW_init = mocker.patch.object(MainWindow, '__init__',
                                                lambda x, y, z: None)

        self.mock_MW_set_brush_radius = mocker.patch.object(MainWindow,
                                                            'set_brush_radius')

        self.mock_MW_draw_brush = mocker.patch.object(MainWindow, 'draw_brush')

        tkinter.messagebox.askyesno = MagicMock(return_value=False)
        tkinter.messagebox.showinfo = MagicMock()
        tkinter.filedialog.askdirectory = MagicMock()
        tkinter.filedialog.askopenfilename = MagicMock()

    @pytest.fixture
    def display_current_patch_mock(self, mocker):
        self.mock_C_display_current_patch = mocker.\
            patch.\
            object(Controller, 'display_current_patch')

    @pytest.fixture
    def dialog_mock(self):
        return mock.patch.object(tkinter.filedialog, "__init__")

    @pytest.fixture
    def mock_brush_radius(self):
        return mock.patch.object(MainWindow, 'set_brush_radius', True)

    def test_get_image_name_from_path(self, setup, display_current_patch_mock,
                                      valid_rgb_image_path):
        """
        Test getting an image's name from its path

        :test_condition: Should be able to get the correct image name from
                         the given path

        :returns: None
        """
        master = MagicMock()
        controller = Controller(master)

        name = controller.get_image_name_from_path(valid_rgb_image_path)

        assert 'KyleS22_mask.png' == name

    def test_get_image_name_from_non_file_path(self, setup,
                                               display_current_patch_mock,
                                               directory_path):
        """

        Test geting an image name when a directory is given

        :test_condition: Should raise a ValueError

        :param directory_path: A path to a directory
        :returns: None
        """

        master = MagicMock()
        controller = Controller(master)

        with pytest.raises(ValueError):
            controller.get_image_name_from_path(directory_path)

    def test_get_landmark_name_from_path(self, setup,
                                         display_current_patch_mock,
                                         valid_rgb_image_path):
        """
        Test getting an image's name from its path

        :test_condition: Should be able to get the correct image name from
                         the given path

        :returns: None
        """
        master = MagicMock()
        controller = Controller(master)

        name = controller.get_landmark_name_from_path(valid_rgb_image_path)

        assert 'KyleS22_labels.npy' == name

    def test_get_landmark_name_from_non_file_path(self, setup,
                                                  display_current_patch_mock,
                                                  directory_path):
        """

        Test geting an image name when a directory is given

        :test_condition: Should raise a ValueError

        :param directory_path: A path to a directory
        :returns: None
        """

        master = MagicMock()
        controller = Controller(master)

        with pytest.raises(ValueError):
            controller.get_landmark_name_from_path(directory_path)

    def test_next_patch_valid_index_displayable(self, setup,
                                                display_current_patch_mock):
        """
        Test moving to the next patch when the current patch is not the last
        patch in the list of patches and the next patch is displayable

        :test_condition: The controller.current_patch is incremented by one

        :returns: None
        """

        master = MagicMock()
        controller = Controller(master)

        controller.current_patch = 0

        mock_patch = MagicMock()
        display_mock = PropertyMock(return_value=True)

        type(mock_patch).display = display_mock

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch,
                                    mock_patch,  mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        controller.next_patch()

        assert controller.current_patch == 1

    def test_next_patch_saved(self, mocker, setup,
                              display_current_patch_mock):
        """
        Test moving to the next patch when the current patch is the last patch
        in the list of patches, and the dialog was not cancelled, and the mask
        has been saved

        :test_condition: Return None
        :returns: None
        """
        mocker.patch.object(Controller, 'save_mask')

        controller = Controller(MagicMock())

        mock_patch = MagicMock()
        display_mock = PropertyMock(return_value=True)

        type(mock_patch).display = display_mock

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch,
                                    mock_patch,  mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image
        controller.current_patch = 2
        controller.mask_saved = True

        result = controller.next_patch()

        assert result is None

    def test_next_patch_valid_index_not_display(self, setup,
                                                display_current_patch_mock):
        """
        Test moving to the next patch when the current patch is not the last
        patch in the list of patches and the next patch is not displayable

        :test_condition: The controller.current_patch is incremented by more
                         than one

        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_patch = 0

        mock_patch = MagicMock()
        display_mock = PropertyMock(return_value=True)

        type(mock_patch).display = display_mock

        mock_no_display_patch = MagicMock()
        false_display_mock = PropertyMock(return_value=False)

        type(mock_no_display_patch).display = false_display_mock

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch,
                                    mock_no_display_patch,  mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        controller.next_patch()

        assert controller.current_patch == 2

    def test_next_patch_invalid_index(self, mocker, setup,
                                      display_current_patch_mock):
        """
        Test moving to the next patch when the current patch is the last patch
        in the list of patches, and the dialog was not cancelled

        :test_condition: A dialog box is created and the current_patch is the
                         same as it was before, and save_mask was called

        :returns: None
        """

        tkinter.messagebox.askyesno = MagicMock()
        tkinter.messagebox.showinfo = MagicMock()

        save_mask_patch = mocker.patch.object(Controller, 'save_mask')

        controller = Controller(MagicMock())

        mocker.patch.object(controller, 'show_saved_preview')

        mock_patch = MagicMock()
        display_mock = PropertyMock(return_value=True)

        type(mock_patch).display = display_mock

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch,
                                    mock_patch,  mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image
        controller.current_patch = 2

        controller.next_patch()

        assert controller.current_patch == 2
        save_mask_patch.assert_called()

    def test_next_patch_invalid_index_dialog(self, mocker, setup,
                                             display_current_patch_mock):
        """
        Test moving to the next patch when the current patch is the last patch
        in the list of patches, and the dialog was cancelled

        :test_condition: A dialog box is created and the current_patch is the
                         same as it was before and save_mask was not called

        :returns: None
        """

        tkinter.messagebox.askyesno = MagicMock(return_value=False)
        tkinter.messagebox.showinfo = MagicMock()

        save_mask_patch = mocker.patch.object(Controller, 'save_mask')

        controller = Controller(MagicMock())

        mocker.patch.object(controller, 'show_saved_preview')

        mock_patch = MagicMock()
        display_mock = PropertyMock(return_value=True)

        type(mock_patch).display = display_mock

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch,
                                    mock_patch,  mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image
        controller.current_patch = 2

        controller.next_patch()

        assert controller.current_patch == 2
        save_mask_patch.assert_not_called()

    def test_prev_patch_valid_index_displayable(self, setup,
                                                display_current_patch_mock):
        """
        Test moving to the previous patch when the current patch is greater
        than 0 and the previous patch is displayable

        :test_condition: The controller.current_patch is decremented by 1

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_patch = 2

        mock_patch = MagicMock()
        display_mock = PropertyMock(return_value=True)

        type(mock_patch).display = display_mock

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch,
                                    mock_patch,  mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        controller.prev_patch()

        assert controller.current_patch == 1

    def test_prev_patch_valid_index_not_display(self, setup,
                                                display_current_patch_mock):
        """
        Test moving to the previous patch when the current patch is greater
        than 0 and the previous patch is not displayable

        :test_condition: The controller.current_patch is decremented by more
                         than 1

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_patch = 2

        mock_patch = MagicMock()
        display_mock = PropertyMock(return_value=True)

        type(mock_patch).display = display_mock

        mock_no_display_patch = MagicMock()
        false_display_mock = PropertyMock(return_value=False)

        type(mock_no_display_patch).display = false_display_mock

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch,
                                    mock_no_display_patch,  mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        controller.prev_patch()

        assert controller.current_patch == 0

    def test_prev_patch_invalid_index(self, setup,
                                      display_current_patch_mock):
        """
        Test moving to thre previous patch when the current patch is 0

        :test_condition: The current_patch remains at 0

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())

        mock_patch = MagicMock()
        thresh_mock = PropertyMock(return_value=0.5)

        type(mock_patch).thresh = thresh_mock

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch, mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        controller.prev_patch()

        assert controller.current_patch == 0

    def test_change_mode_thresh(self, setup, mocker,
                                display_current_patch_mock):
        """
        Test changing the mode to Threshold

        :test_condition: The current mode is set to Mode.THRESHOLD and
                         MainWindow.set_brush_radius is called once

        :param setup: The setup fixture
        :param mock_brush_radius: A fixture mocking the
                                  MainWindow.set_brush_radius function
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.ADD_REGION

        mock_patch = MagicMock()
        thresh_mock = PropertyMock(return_value=0.5)

        type(mock_patch).thresh = thresh_mock

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        spy = mocker.spy(MainWindow, 'set_brush_radius')

        controller.change_mode(MainWindow.ID_TOOL_THRESH)

        spy.assert_called_once()

        assert controller.current_mode == Mode.THRESHOLD

    def test_change_mode_add_region(self, setup, mocker):
        """
        Test changing the mode to add region

        :test_condition: The current mode is set to Mode.ADD_REGION and
                         MainWindow.set_brush_radius is called once

        :param setup: The setup fixture
        :param mock_brush_radius: A fixture mocking the
                                  MainWindow.set_brush_radius function
        :returns: None
        """
        controller = Controller(MagicMock())
        controller.current_mode = Mode.THRESHOLD

        mock_patch = MagicMock()
        thresh_mock = PropertyMock(return_value=0.5)

        type(mock_patch).thresh = thresh_mock

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        spy = mocker.spy(MainWindow, 'set_brush_radius')

        controller.change_mode(MainWindow.ID_TOOL_ADD)

        spy.assert_called_once()

        assert controller.current_mode == Mode.ADD_REGION

    def test_change_mode_remove_region(self, setup, mocker):
        """
        Test changing the mode to remove region

        :test_condition: The current mode is set to Mode.REMOVE_REGION and
                         MainWindow.set_brush_radius is called once

        :param setup: The setup fixture
        :param mock_brush_radius: A fixture mocking the
                                  MainWindow.set_brush_radius function
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.THRESHOLD

        mock_patch = MagicMock()
        thresh_mock = PropertyMock(return_value=0.5)

        type(mock_patch).thresh = thresh_mock

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        spy = mocker.spy(MainWindow, 'set_brush_radius')

        controller.change_mode(MainWindow.ID_TOOL_REMOVE)

        spy.assert_called_once()

        assert controller.current_mode == Mode.REMOVE_REGION

    def test_change_mode_no_root_activate(self, setup, mocker,
                                          display_current_patch_mock):
        """
        Test changing the mode to NO ROOT

        :test_condition:  The no_root_activate function is called

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.THRESHOLD

        mock_patch = MagicMock()
        thresh_mock = PropertyMock(return_value=0.5)

        type(mock_patch).thresh = thresh_mock

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        spy = mocker.spy(controller, 'no_root_activate')

        controller.change_mode(MainWindow.ID_TOOL_NO_ROOT)

        spy.assert_called_once()

    def test_change_mode_zoom(self, setup, mocker,
                              display_current_patch_mock):
        """
        Test changing the mode to zoom

        :test_condition: The current mode is set to Mode.ZOOM and
                         MainWindow.set_brush_radius is called once

        :param setup: The setup fixture
        :param mock_brush_radius: A fixture mocking the
                                  MainWindow.set_brush_radius function
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.ADD_REGION

        mock_patch = MagicMock()
        thresh_mock = PropertyMock(return_value=0.5)

        type(mock_patch).thresh = thresh_mock

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        spy = mocker.spy(MainWindow, 'set_brush_radius')

        controller.change_mode(MainWindow.ID_TOOL_ZOOM)

        spy.assert_called_once()

        assert controller.current_mode == Mode.ZOOM

    def test_change_mode_flood_add(self, setup, mocker,
                                   display_current_patch_mock):
        """
        Test changing the mode to Flood Add

        :test_condition: The current mode is set to Mode.FLOOD_ADD

        :param setup: The setup fixture
        :param mock_brush_radius: A fixture mocking the
                                  MainWindow.set_brush_radius function
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.ADD_REGION

        mock_patch = MagicMock()
        thresh_mock = PropertyMock(return_value=0.5)

        type(mock_patch).thresh = thresh_mock

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        controller.change_mode(MainWindow.ID_TOOL_FLOOD_ADD)

        assert controller.current_mode == Mode.FLOOD_ADD

    def test_change_mode_flood_remove(self, setup, mocker,
                                      display_current_patch_mock):
        """
        Test changing the mode to Flood Remove

        :test_condition: The current mode is set to Mode.FLOOD_REMOVE

        :param setup: The setup fixture
        :param mock_brush_radius: A fixture mocking the
                                  MainWindow.set_brush_radius function
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.ADD_REGION

        mock_patch = MagicMock()
        thresh_mock = PropertyMock(return_value=0.5)

        type(mock_patch).thresh = thresh_mock

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        controller.change_mode(MainWindow.ID_TOOL_FLOOD_REMOVE)

        assert controller.current_mode == Mode.FLOOD_REMOVE

    def test_change_mode_add_tip(self, setup, mocker,
                                 display_current_patch_mock):
        """
        Test changing the mode to Add Tip

        :test_condition: The current mode is set to Mode.ADD_TIP

        :param setup: The setup fixture
        :param mock_brush_radius: A fixture mocking the
                                  MainWindow.set_brush_radius function
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.ADD_REGION

        mock_patch = MagicMock()
        thresh_mock = PropertyMock(return_value=0.5)

        type(mock_patch).thresh = thresh_mock

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        controller.change_mode(MainWindow.ID_TOOL_ADD_TIP)

        assert controller.current_mode == Mode.ADD_TIP

    def test_change_mode_add_cross(self, setup, mocker,
                                   display_current_patch_mock):
        """
        Test changing the mode to Add Cross

        :test_condition: The current mode is set to Mode.ADD_CROSS

        :param setup: The setup fixture
        :param mock_brush_radius: A fixture mocking the
                                  MainWindow.set_brush_radius function
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.ADD_REGION

        mock_patch = MagicMock()
        thresh_mock = PropertyMock(return_value=0.5)

        type(mock_patch).thresh = thresh_mock

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        controller.change_mode(MainWindow.ID_TOOL_ADD_CROSS)

        assert controller.current_mode == Mode.ADD_CROSSING

    def test_change_mode_add_branch(self, setup, mocker,
                                    display_current_patch_mock):
        """
        Test changing the mode to Add Branch

        :test_condition: The current mode is set to Mode.ADD_BRANCH

        :param setup: The setup fixture
        :param mock_brush_radius: A fixture mocking the
                                  MainWindow.set_brush_radius function
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.ADD_REGION

        mock_patch = MagicMock()
        thresh_mock = PropertyMock(return_value=0.5)

        type(mock_patch).thresh = thresh_mock

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        controller.change_mode(MainWindow.ID_TOOL_ADD_BRANCH)

        assert controller.current_mode == Mode.ADD_BRANCH

    def test_change_mode_remove_landmark(self, setup, mocker,
                                         display_current_patch_mock):
        """
        Test changing the mode to Remove Landmark

        :test_condition: The current mode is set to Mode.REMOVE_LANDMARK

        :param setup: The setup fixture
        :param mock_brush_radius: A fixture mocking the
                                  MainWindow.set_brush_radius function
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.ADD_REGION

        mock_patch = MagicMock()
        thresh_mock = PropertyMock(return_value=0.5)

        type(mock_patch).thresh = thresh_mock

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        controller.change_mode(MainWindow.ID_TOOL_REMOVE_LANDMARK)

        assert controller.current_mode == Mode.REMOVE_LANDMARK

    def test_change_mode_invalid(self, setup, mocker):
        """
        Test changing the mode to an invalid mode

        :param setup: The setup fixture
        :param mocker: Mocker
        :returns: None
        """
        controller = Controller(MagicMock())

        result = controller.change_mode(-1)
        assert False is result

    def test_no_root_activate(self, setup, display_current_patch_mock):
        """
        Test calling no_root activate

        :test_condition: The patch clear_mask and overlay mask functions are
                         called

        :param setup: The setup fixture
        :returns: None
        """
        controller = Controller(MagicMock())
        controller.current_mode = Mode.THRESHOLD

        mock_patch = MagicMock()
        thresh_mock = PropertyMock(return_value=0.5)

        type(mock_patch).thresh = thresh_mock

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        controller.no_root_activate()

        mock_patch.clear_mask.assert_called()
        mock_patch.overlay_mask.assert_called()

    def test_handle_mouse_wheel_threshold(self, setup, mocker,
                                          display_current_patch_mock):
        """
        Test when the mouse wheel function is called and the current mode is
        Mode.THRESHOLD

        :test_condition: The adjust threshold function is called
                         and the function returns True

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.THRESHOLD

        mock_patch = MagicMock()
        thresh_mock = PropertyMock(return_value=0.5)

        type(mock_patch).thresh = thresh_mock

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        spy = mocker.spy(controller, 'adjust_threshold')

        result = controller.handle_mouse_wheel(-1, 0, 0)

        spy.assert_called_once_with(-1)
        assert True is result

    def test_handle_mouse_wheel_add_region(self, setup, mocker,
                                           display_current_patch_mock):
        """
        Test when the mouse wheel function is called and the current mode is
        Mode.ADD_REGION

        :test_condition: The adjust_add_region_brush function is called
                         and the function returns True

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.ADD_REGION

        spy = mocker.spy(controller, 'adjust_add_region_brush')

        result = controller.handle_mouse_wheel(-1, 0, 0)

        spy.assert_called_once_with(-1)
        assert True is result

    def test_handle_mouse_wheel_remove_region(self, setup, mocker,
                                              display_current_patch_mock):
        """
        Test when the mouse wheel function is called and the current mode is
        Mode.REMOVE_REGION

        :test_condition: The adjust_remove_region_brush funtion is called
                         and the function returns True

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.REMOVE_REGION

        spy = mocker.spy(controller, 'adjust_remove_region_brush')

        result = controller.handle_mouse_wheel(-1, 0, 0)

        spy.assert_called_once_with(-1)
        assert True is result

    def test_handle_mouse_wheel_zoom(self, setup, mocker,
                                     display_current_patch_mock):
        """
        Test when the mouse wheel function is called and the current mode is
        Mode.ZOOM

        :test_condition: The adjust handle_zoom function is called
                         and the function returns True
        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.ZOOM
        controller.main_window = MagicMock()
        controller.main_window.image_scale = 1
        controller.main_window.MAX_SCALE = 16
        controller.main_window.MIN_SCALE = 0.25

        mock_patch = MagicMock()
        thresh_mock = PropertyMock(return_value=0.5)

        type(mock_patch).thresh = thresh_mock

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        spy = mocker.spy(controller, 'handle_zoom')

        result = controller.handle_mouse_wheel(-1, 0, 0)

        spy.assert_called_once_with(-1, 0, 0)
        assert True is result

    def test_handle_mouse_wheel_flood_add(self, setup, mocker,
                                          display_current_patch_mock):
        """
        Test when the mouse wheel function is called and the current mode is
        Mode.FLOOD_ADD

        :test_condition: The handle_flood_add_tolerance function is called

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.FLOOD_ADD
        controller.flood_add_position = (0, 0)

        mock_patch = MagicMock()
        thresh_mock = PropertyMock(return_value=0.5)

        type(mock_patch).thresh = thresh_mock

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        spy = mocker.spy(controller, 'handle_flood_add_tolerance')

        controller.handle_mouse_wheel(-1, 0, 0)

        spy.assert_called_once_with(-1)

    def test_handle_mouse_wheel_flood_remove(self, setup, mocker,
                                             display_current_patch_mock):
        """
        Test when the mouse wheel function is called and the current mode is
        Mode.FLOOD_REMOVE

        :test_condition: The handle_flood_remove_tolerance function is called

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.FLOOD_REMOVE
        controller.flood_remove_position = (0, 0)

        mock_patch = MagicMock()
        thresh_mock = PropertyMock(return_value=0.5)

        type(mock_patch).thresh = thresh_mock

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        spy = mocker.spy(controller, 'handle_flood_remove_tolerance')

        controller.handle_mouse_wheel(-1, 0, 0)

        spy.assert_called_once_with(-1)

    def test_handle_mouse_wheel_remove_landmark(self, setup, mocker,
                                                display_current_patch_mock):
        """
        Test when the mouse wheel function is called and the current mode is
        Mode.REMOVE_LANDMARK

        :test_condition: The adjust_remove_landmark_brush function is called
                         and the function returns True

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.REMOVE_LANDMARK

        spy = mocker.spy(controller, 'adjust_remove_landmark_brush')

        result = controller.handle_mouse_wheel(-1, 0, 0)

        spy.assert_called_once_with(-1)
        assert True is result

    def test_handle_mouse_wheel_invalid(self, setup,
                                        display_current_patch_mock):
        """
        Test when the mouse wheel function is called and the current mode is
        invalid

        :test_condition: The function returns False

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.NO_ROOT

        result = controller.handle_mouse_wheel(-1, 0, 0)

        assert False is result

    def test_handle_flood_add_tolerance_none_pos(self, setup,
                                                 display_current_patch_mock):
        """
        Test when the handle flood add tolerance function is called and the
        current flood_add_position is None

        :test_condition: Return None and flood_add_tolerance does not change

        :param self: Self
        :param setup: Setup
        :param display_current_patch_mock: Mock for display current patch
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.flood_add_position = None
        controller.image = MagicMock()

        old_tol = controller.flood_add_tolerance

        controller.handle_flood_add_tolerance(-1)

        assert controller.flood_add_tolerance == old_tol

    def test_handle_flood_add_tolerance_pos_rot(self, setup,
                                                display_current_patch_mock):
        """
        Test when the handle flood add tolerance function is called and the
        rotation is positive

        :test_condition: Return None and flood_add_tolerance is increased

        :param self: Self
        :param setup: Setup
        :param display_current_patch_mock: Mock for display current patch
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.flood_add_position = (0, 0)
        controller.image = MagicMock()

        old_tol = controller.flood_add_tolerance

        controller.handle_flood_add_tolerance(1)

        assert controller.flood_add_tolerance > old_tol

    def test_handle_flood_remove_tolerance_no_pos(self, setup,
                                                  display_current_patch_mock):
        """
        Test when the handle flood remove tolerance function is called and the
        current flood_remove_position is None

        :test_condition: Return None and flood_remove_tolerance does not change

        :param self: Self
        :param setup: Setup
        :param display_current_patch_mock: Mock for display current patch
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.flood_remove_position = None
        controller.image = MagicMock()

        old_tol = controller.flood_remove_tolerance

        controller.handle_flood_remove_tolerance(-1)

        assert controller.flood_remove_tolerance == old_tol

    def test_handle_flood_remove_tolerance_pos_rot(self, setup,
                                                   display_current_patch_mock):
        """
        Test when the handle flood remove tolerance function is called and the
        rotation is positive

        :test_condition: Return None and flood_remove_tolerance is increased

        :param self: Self
        :param setup: Setup
        :param display_current_patch_mock: Mock for display current patch
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.flood_remove_position = (0, 0)
        controller.image = MagicMock()

        old_tol = controller.flood_remove_tolerance

        controller.handle_flood_remove_tolerance(1)

        assert controller.flood_remove_tolerance > old_tol

    def test_handle_flood_remove_tolerance_neg_rot(self, setup,
                                                   display_current_patch_mock):
        """
        Test when the handle flood remove tolerance function is called and the
        rotation is negative

        :test_condition: flood_remove_tolerance is decreased

        :param self: Self
        :param setup: Setup
        :param display_current_patch_mock: Mock for display current patch
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.flood_remove_position = (0, 0)
        controller.image = MagicMock()

        old_tol = controller.flood_remove_tolerance

        controller.handle_flood_remove_tolerance(-1)

        assert controller.flood_remove_tolerance < old_tol

    def test_handle_flood_add_tolerance_neg_rot(self, setup,
                                                display_current_patch_mock):
        """
        Test when the handle flood add tolerance function is called and the
        rotation is negative

        :test_condition: Return None and flood_add_tolerance is decreased

        :param self: Self
        :param setup: Setup
        :param display_current_patch_mock: Mock for display current patch
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.flood_add_position = (0, 0)
        controller.image = MagicMock()

        old_tol = controller.flood_add_tolerance

        controller.handle_flood_add_tolerance(-1)

        assert controller.flood_add_tolerance < old_tol

    def test_handle_flood_add_tolerance_zero_rot(self, setup,
                                                 display_current_patch_mock):
        """
        Test when the handle flood add tolerance function is called and the
        rotation is zero

        :test_condition: Return None and flood_add_tolerance is not changed

        :param self: Self
        :param setup: Setup
        :param display_current_patch_mock: Mock for display current patch
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.flood_add_position = (0, 0)
        controller.image = MagicMock()

        old_tol = controller.flood_add_tolerance

        controller.handle_flood_add_tolerance(0)

        assert controller.flood_add_tolerance == old_tol

    def test_handle_flood_remove_tol_zero_rot(self, setup,
                                              display_current_patch_mock):
        """
        Test when the handle flood remove tolerance function is called and the
        rotation is zero

        :test_condition: Return None and flood_remove_tolerance is not changed

        :param self: Self
        :param setup: Setup
        :param display_current_patch_mock: Mock for display current patch
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.flood_remove_position = (0, 0)
        controller.image = MagicMock()

        old_tol = controller.flood_remove_tolerance

        controller.handle_flood_remove_tolerance(0)

        assert controller.flood_remove_tolerance == old_tol

    def test_handle_left_click_add_region(self, setup,
                                          display_current_patch_mock):
        """
        Test when the left mouse button is clicked and the current mode is
        Mode.ADD_REGION

        :test_condition: The patch.add_region_function is called with the given
                         position and the current add_region_radius, and
                         returns True

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.ADD_REGION
        controller.main_window = MagicMock()
        controller.main_window.image_scale = 1
        controller.main_window.image_x = 0
        controller.main_window.image_y = 0

        mock_patch = MagicMock()

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        position = (1, 2)
        radius = controller.add_region_radius

        result = controller.handle_left_click(position)

        mock_patch.add_region.assert_called_with(position, radius)
        assert True is result

    def test_handle_left_click_remove_region(self, setup,
                                             display_current_patch_mock):
        """
        Test when the left mouse button is clicked and the current mode is
        Mode.REMOVE_REGION

        :test_condition: The patch.remove_region functin is called with the
                         given position and the current remove_region_radius
                         and returns True


        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.REMOVE_REGION
        controller.main_window = MagicMock()
        controller.main_window.image_scale = 1
        controller.main_window.image_x = 0
        controller.main_window.image_y = 0

        mock_patch = MagicMock()

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        position = (1, 2)
        radius = controller.remove_region_radius

        result = controller.handle_left_click(position)

        mock_patch.remove_region.assert_called_with(position, radius)
        assert True is result

    def test_handle_left_click_flood_add(self, setup,
                                         display_current_patch_mock):
        """
        Test when the left mouse button is clicked and the current mode is
        Mode.FLOOD_ADD

        :test_condition: The patch.flood_add_region is called with the given
                         position and the current flood_add_tolerance

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.FLOOD_ADD
        controller.main_window = MagicMock()
        controller.main_window.image_scale = 1
        controller.main_window.image_x = 0
        controller.main_window.image_y = 0

        mock_patch = MagicMock()

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        position = (1, 2)
        tolerance = controller.flood_add_tolerance

        controller.handle_left_click(position)

        mock_patch.flood_add_region.assert_called_with(position, tolerance)

    def test_handle_left_click_flood_remove(self, setup,
                                            display_current_patch_mock):
        """
        Test when the left mouse button is clicked and the current mode is
        Mode.FLOOD_REMOVE

        :test_condition: The patch.flood_remove_region is called with the given
                         position and the current flood_remove_tolerance

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.FLOOD_REMOVE
        controller.main_window = MagicMock()
        controller.main_window.image_scale = 1
        controller.main_window.image_x = 0
        controller.main_window.image_y = 0

        mock_patch = MagicMock()

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        position = (1, 2)
        tolerance = controller.flood_remove_tolerance

        controller.handle_left_click(position)

        mock_patch.flood_remove_region.assert_called_with(position, tolerance)

    def test_handle_left_click_add_tip(self, setup,
                                       display_current_patch_mock):
        """
        Test when the left mouse button is clicked and the current mode is
        Mode.ADD_TIP

        :test_condition: The patch.add_landmark_function is
                         called with the given
                         position and the current add_tip_radius, and
                         returns True

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.ADD_TIP
        controller.main_window = MagicMock()
        controller.main_window.image_scale = 1
        controller.main_window.image_x = 0
        controller.main_window.image_y = 0

        mock_patch = MagicMock()

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        position = (1, 2)
        radius = controller.add_tip_radius

        result = controller.handle_left_click(position)

        mock_patch.add_landmark.assert_called_with(position, radius,
                                                   mock_image.TIP_LABEL)
        assert True is result

    def test_handle_left_click_add_cross(self, setup,
                                         display_current_patch_mock):
        """
        Test when the left mouse button is clicked and the current mode is
        Mode.ADD_CROSSING

        :test_condition: The patch.add_landmark_function is called
                         with the given
                         position and the current add_cross_radius, and
                         returns True

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.ADD_CROSSING
        controller.main_window = MagicMock()
        controller.main_window.image_scale = 1
        controller.main_window.image_x = 0
        controller.main_window.image_y = 0

        mock_patch = MagicMock()

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        position = (1, 2)
        radius = controller.add_cross_radius

        result = controller.handle_left_click(position)

        mock_patch.add_landmark.assert_called_with(position, radius,
                                                   mock_image.CROSS_LABEL)
        assert True is result

    def test_handle_left_click_add_branch(self, setup,
                                          display_current_patch_mock):
        """
        Test when the left mouse button is clicked and the current mode is
        Mode.ADD_BRANCH

        :test_condition: The patch.add_landmark_function is called with
                         the given
                         position and the current add_branch_radius, and
                         returns True

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.ADD_BRANCH
        controller.main_window = MagicMock()
        controller.main_window.image_scale = 1
        controller.main_window.image_x = 0
        controller.main_window.image_y = 0

        mock_patch = MagicMock()

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        position = (1, 2)
        radius = controller.add_branch_radius

        result = controller.handle_left_click(position)

        mock_patch.add_landmark.assert_called_with(position, radius,
                                                   mock_image.BRANCH_LABEL)
        assert True is result

    def test_handle_left_click_remove_landmark(self, setup,
                                               display_current_patch_mock):
        """
        Test when the left mouse button is clicked and the current mode is
        Mode.REMOVE_LANDMARK

        :test_condition: The patch.remove_landmark_function is called with the
                         given
                         position and the current remove_landmark_radius, and
                         returns True

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.REMOVE_LANDMARK
        controller.main_window = MagicMock()
        controller.main_window.image_scale = 1
        controller.main_window.image_x = 0
        controller.main_window.image_y = 0

        mock_patch = MagicMock()

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        position = (1, 2)
        radius = controller.remove_landmark_radius

        result = controller.handle_left_click(position)

        mock_patch.remove_landmark.assert_called_with(position, radius)
        assert True is result

    def test_handle_left_click_invalid_mode(self, setup,
                                            display_current_patch_mock):
        """
        Test when the left mouse button is clicked and the current mode is
        Mode.THRESHOLD

        :test_condition: The function should return False

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.THRESHOLD
        controller.main_window = MagicMock()
        controller.main_window.image_scale = 1
        controller.main_window.image_x = 0
        controller.main_window.image_y = 0

        result = controller.handle_left_click((10, 10))
        assert False is result

    def test_handle_left_click_out_of_bounds(self, setup,
                                             display_current_patch_mock):
        """
        Test when clicking off of the image

        :test condition: Returns False

        :param setup: Setup
        :param display_current_patch_mock: Mock for displaying the patch
        :returns: None
        """
        controller = Controller(MagicMock())
        controller.current_mode = Mode.THRESHOLD
        controller.main_window = MagicMock()
        controller.main_window.image_scale = 1
        controller.main_window.image_x = 0
        controller.main_window.image_y = 0

        result = controller.handle_left_click((-10, 10))
        assert False is result

        result = controller.handle_left_click((10, -10))
        assert False is result

    def test_handle_right_click_zoom(self, setup, display_current_patch_mock):
        """
        Test when a right click happens while zooming

        :test_condition: The main_window.image_scale is set to 1, and the
                         main_window.image_x and image_y are set to 0

        :param setup: Setup
        :param display_current_patch_mock: Mock for displaying the current
                                           patch
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.ZOOM
        controller.main_window = MagicMock()
        controller.main_window.image_scale = 10
        controller.main_window.image_x = 10
        controller.main_window.image_y = 10

        controller.handle_right_click()

        assert controller.main_window.image_scale == 1
        assert controller.main_window.image_x == 0
        assert controller.main_window.image_y == 0

    def test_handle_right_click_other(self, setup, display_current_patch_mock):
        """
        Test when a right click happens while not zooming

        :test_condition: main_window.image_x image_y, and image_scale are
                         not changed

        :param setup: Setup
        :param display_current_patch_mock: Mock for displaying the current
                                           patch
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.ADD_REGION
        controller.main_window = MagicMock()
        controller.main_window.image_scale = 10
        controller.main_window.image_x = 10
        controller.main_window.image_y = 10

        controller.handle_right_click()

        assert controller.main_window.image_scale == 10
        assert controller.main_window.image_x == 10
        assert controller.main_window.image_y == 10

    def test_handle_left_release_add_region(self, setup,
                                            display_current_patch_mock):
        """
        Test when the mouse is released and the current mode is Mode.ADD_REGION

        :test_condition:  The function returns True

        :param setup: The setup ficture
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.ADD_REGION

        result = controller.handle_left_release()

        assert True is result

    def test_handle_left_release_remove_region(self, setup,
                                               display_current_patch_mock):
        """
        Test when the mouse is released and the current mode is
        Mode.REMOVE_REGION

        :test_condition: The function returns True

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.REMOVE_REGION

        result = controller.handle_left_release()

        assert True is result

    def test_handle_left_release_zoom(self, setup, mocker,
                                      display_current_patch_mock):
        """
        Test when the mouse is released and the current mode is Mode.ZOOM

        :test_condition:  display_current_patch() is called and the function
                          returns True

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.ZOOM

        result = controller.handle_left_release()

        assert True is result
        self.mock_C_display_current_patch.assert_called_once()

    def test_handle_left_release_invalid_mode(self, setup,
                                              display_current_patch_mock):
        """
        Test when the mouse is released and the current mode is not ADD or
        REMOVE REGION

        :test_condition: The function returns False

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.THRESHOLD

        result = controller.handle_left_release()
        assert False is result

    def test_handle_motion_add_region(self, setup, display_current_patch_mock):
        """
        Test when the mouse is moved and the current mode is Mode.ADD_REGION

        :test_condition: The patch add_region function is called with the given
                         position and the current add_region_radius
                         and returns True

        :param setup: The setip fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.ADD_REGION
        controller.main_window = MagicMock()
        controller.main_window.image_scale = 1
        controller.main_window.image_x = 0
        controller.main_window.image_y = 0

        mock_patch = MagicMock()

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        position = (1, 2)
        radius = (controller.add_region_radius /
                  controller.main_window.image_scale)

        result = controller.handle_motion(position)

        mock_patch.add_region.assert_called_with(position, radius)
        assert True is result

    def test_handle_motion_remove_region(self, setup, mocker,
                                         display_current_patch_mock):
        """
        Test when the mouse is moved and the current mode is Mode.REMOVE_REGION

        :test_condition: The patch remove_region function is called with the
                         given position and the current remove_region_radius
                         and returns True

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.REMOVE_REGION
        controller.main_window = MagicMock()
        controller.main_window.image_scale = 1
        controller.main_window.image_x = 0
        controller.main_window.image_y = 0

        mock_patch = MagicMock()

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        position = (1, 2)

        radius = (controller.remove_region_radius /
                  controller.main_window.image_scale)

        result = controller.handle_motion(position)

        mock_patch.remove_region.assert_called_with(position, radius)
        assert True is result

    def test_handle_motion_zoom(self, setup, display_current_patch_mock):
        """
        Test when the mouse is moved and the current mode is Mode.ZOOM

        :test_condition: Returns True

        :param setup: The setip fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.ZOOM
        controller.main_window = MagicMock()
        controller.main_window.image_scale = 1
        controller.main_window.image_x = 0
        controller.main_window.image_y = 0

        mock_patch = MagicMock()

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        position = (1, 2)

        result = controller.handle_motion(position)

        assert True is result

    def test_handle_motion_remove_landmark(self, setup,
                                           display_current_patch_mock):
        """
        Test when the mouse is moved and the current mode is
        Mode.REMOVE_LANDMARK

        :test_condition: The patch remove_landmark function is called with
                         the given
                         position and the current remove_landmark_radius
                         and returns True

        :param setup: The setip fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.REMOVE_LANDMARK
        controller.main_window = MagicMock()
        controller.main_window.image_scale = 1
        controller.main_window.image_x = 0
        controller.main_window.image_y = 0

        mock_patch = MagicMock()

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[mock_patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        position = (1.0, 2.0)
        radius = (controller.remove_landmark_radius /
                  controller.main_window.image_scale)

        result = controller.handle_motion(position)

        mock_patch.remove_landmark.assert_called_with(position, radius)
        assert True is result

    def test_handle_motion_invalid_mode(self, setup,
                                        display_current_patch_mock):
        """
        Test when the mouse is moved and the current mode is not ADD or REMOVE
        REGION

        :test_condition: Should return False

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_mode = Mode.THRESHOLD
        controller.main_window = MagicMock()
        controller.main_window.image_scale = 1
        controller.main_window.image_x = 0
        controller.main_window.image_y = 0

        result = controller.handle_motion((10, 10))

        assert False is result

    def test_handle_motion_out_of_bounds(self, setup,
                                         display_current_patch_mock):
        """
        Test when dragging off of the image

        :test condition: Returns False

        :param setup: Setup
        :param display_current_patch_mock: Mock for displaying the patch
        :returns: None
        """
        controller = Controller(MagicMock())
        controller.current_mode = Mode.THRESHOLD
        controller.main_window = MagicMock()
        controller.main_window.image_scale = 1
        controller.main_window.image_x = 0
        controller.main_window.image_y = 0

        result = controller.handle_motion((-10, 10))
        assert False is result

        result = controller.handle_motion((10, -10))
        assert False is result

    def test_adjust_threshold_pos_rot_valid_thresh(self, setup,
                                                   test_image_data,
                                                   display_current_patch_mock):
        """
        Test when the mouse wheel has a positive rotation in Mode.THRESHOLD
        and the threshold is greater than 0
        :test_condition: The patches thresh value should be decreased by 0.01

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        patch = Patch(test_image_data, (0, 0))
        patch.thresh = 0.5

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        old_threshold = controller\
            .image.patches[controller.current_patch].thresh

        controller.adjust_threshold(1)

        new_patch = controller.image.patches[controller.current_patch]

        assert (old_threshold - 0.01) == new_patch.thresh

    def test_adjust_thresh_pos_rot_invalid_thresh(self, setup,
                                                  test_image_data,
                                                  display_current_patch_mock):
        """
        Test when the mouse wheel has a positive rotation in Mode.THRESHOLD
        and the threshold is smaller than or equal to 0

        :test_condition: The patches thresh value should not be changed

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        patch = Patch(test_image_data, (0, 0))
        patch.thresh = 0.0

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        old_threshold = controller\
            .image.patches[controller.current_patch].thresh

        controller.adjust_threshold(1)

        new_patch = controller.image.patches[controller.current_patch]

        assert old_threshold == new_patch.thresh

    def test_adjust_thresh_neg_rot_invalid_thresh(self, setup,
                                                  test_image_data,
                                                  display_current_patch_mock):
        """
        Test when the mouse wheel has a negative rotation in Mode.THRESHOLD
        and the threshold is greater than or equal to one

        :test_condition: The patches thresh value should not be changed

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        patch = Patch(test_image_data, (0, 0))
        patch.thresh = 1.0

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        old_threshold = controller\
            .image.patches[controller.current_patch].thresh

        controller.adjust_threshold(-1)

        new_patch = controller.image.patches[controller.current_patch]

        assert old_threshold == new_patch.thresh

    def test_adjust_thresh_neg_rot_valid_thresh(self, setup,
                                                test_image_data,
                                                display_current_patch_mock):
        """
        Test when the mouse wheel has a negative rotation in Mode.THRESHOLD
        and the threshold is less than one

        :test_condition: The patches thresh value should be increased by 0.01

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        patch = Patch(test_image_data, (0, 0))
        patch.thresh = 0.5

        mock_image = MagicMock()
        patches_mock = PropertyMock(return_value=[patch])

        type(mock_image).patches = patches_mock

        controller.image = mock_image

        old_threshold = controller\
            .image.patches[controller.current_patch].thresh

        controller.adjust_threshold(-1)

        new_patch = controller.image.patches[controller.current_patch]

        assert old_threshold != new_patch.thresh
        assert (old_threshold + 0.01) == new_patch.thresh

    def test_adjust_add_region_brush_positive_rot(self, setup):
        """
        Test when the mouse wheel has a positive rotation in Mode.ADD_REGION

        :test_condition: The add_region_radius is increased by 1

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())

        old_add_radius = controller.add_region_radius

        controller.adjust_add_region_brush(1)

        assert controller.add_region_radius != old_add_radius
        assert (controller.add_region_radius - 1) == old_add_radius

    def test_adjust_add_region_brush_negative_rot(self, setup):
        """
        Test when the mouse wheel has a negative rotation in Mode.ADD_REGION

        :test_condition: The add_region_radius is decreased by 1

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())

        old_add_radius = controller.add_region_radius

        controller.adjust_add_region_brush(-1)

        assert controller.add_region_radius != old_add_radius
        assert (controller.add_region_radius + 1) == old_add_radius

    def test_adjust_remove_region_brush_positive_rot(self, setup):
        """
        Test when the mouse wheel has a positive rotation in Mode.REMOVE_REGION

        :test_condition: The remove_region_radius is increased by 1

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())

        old_remove_radius = controller.remove_region_radius

        controller.adjust_remove_region_brush(1)

        assert controller.remove_region_radius != old_remove_radius
        assert (controller.remove_region_radius - 1) == old_remove_radius

    def test_adjust_remove_region_brush_negative_rot(self, setup):
        """
        Test when the mouse wheel has a negative rotation in Mode.REMOVE_REGION

        :test_condition: The remove_region_radius is decreased by 1

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())

        old_remove_radius = controller.remove_region_radius

        controller.adjust_remove_region_brush(-1)

        assert controller.remove_region_radius != old_remove_radius
        assert (controller.remove_region_radius + 1) == old_remove_radius

    def test_load_new_image_no_cancel(self, setup, mocker,
                                      display_current_patch_mock):
        """
        Test loading a new image

        :test_condition: current_patch is set to 0,
                         and display_current_patch is called

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_patch = 5
        mocker.patch('friendly_ground_truth.view.tk_view.MainWindow.'
                     'start_progressbar')
        mocker.patch('friendly_ground_truth.model.model.Image.__init__',
                     return_value=None)

        spy = mocker.spy(controller, 'display_current_patch')

        controller.load_new_image()

        spy.assert_called_once()
        assert controller.current_patch == 0

    def test_load_new_image_cancel(self, setup, mocker):
        """
        Test loading a new image when the user cancels

        :test_condition: current_patch is not changed,
                         and display_current_patch is not called

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_patch = 5

        tkinter.filedialog.askopenfilename = MagicMock(return_value=None)

        mocker.patch('friendly_ground_truth.model.model.Image.__init__',
                     return_value=None)

        # fd = file_dialog_patch.return_value.__enter__.return_value

        spy = mocker.spy(controller, 'display_current_patch')
        mocker.patch.object(controller, 'display_current_patch')

        controller.load_new_image()

        spy.assert_not_called()
        assert controller.current_patch == 5

    def test_load_new_image_except(self, setup, mocker):
        """
        Test loading a new image when the file cannot be loaded

        :test_condition: current_patch is not changed,
                         and display_current_patch is not called

        :param setup: The setup fixture
        :returns: None
        """

        def raise_FileNotFound(args, kwargs):
            raise FileNotFoundError

        mocker.patch("friendly_ground_truth.controller.controller.Controller."
                     "update_progress_bar")

        mocker.patch("friendly_ground_truth.view.tk_view.MainWindow."
                     "start_progressbar")

        controller = Controller(MagicMock())
        controller.current_patch = 5

        image_mock = mocker.patch('friendly_ground_truth.model' +
                                  '.model.Image.__init__',
                                  return_value=None)

        image_mock.side_effect = raise_FileNotFound

        spy = mocker.spy(controller, 'display_current_patch')

        controller.load_new_image()

        spy.assert_not_called()
        assert controller.current_patch == 5

    def test_update_progressbar_not_done(self, setup, mocker):
        """
        Test updating the progressbar when there are still more patches to load

        :test_condition: window.prog_popup.update() is called

        :param setup: setup
        :param mocker: Mocker
        :returns: None
        """
        controller = Controller(MagicMock())
        controller.main_window.prog_popup = MagicMock()
        controller.main_window.load_progress = 0
        controller.main_window.progress_step = 10
        controller.main_window.load_prog_var = MagicMock()
        controller.update_progress_bar()

        controller.main_window.prog_popup.update.assert_called()
        controller.main_window.prog_popup.destroy.assert_not_called()

    def test_update_progressbar_done(self, setup, mocker):
        """
        Test updating the progressbar when there are no more patches to load

        :test_condition: window.prog_popup.destroy() is called

        :param setup: setup
        :param mocker: Mocker
        :returns: None
        """
        controller = Controller(MagicMock())
        controller.main_window.prog_popup = MagicMock()
        controller.main_window.load_progress = (Image.NUM_PATCHES ** 2) - 1
        controller.main_window.progress_step = 1
        controller.main_window.load_prog_var = MagicMock()
        controller.update_progress_bar()

        controller.main_window.prog_popup.destroy.assert_called()

    def test_save_mask_no_cancel(self, setup, mocker):
        """
        Test saving the mask

        :test_condition: image.export_mask() is called

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.current_patch = 5

        # fd = file_dialog_patch.return_value.__enter__.return_value

        # fd.GetPath.return_value = 'fake/path/test.png'

        mock_image = MagicMock()

        controller.image = mock_image
        controller.image_path = '/this/is/a/path.png'
        controller.save_mask()

        mock_image.export_mask.assert_called()

    def test_save_mask_cancel(self, setup, mocker):
        """
        Test exporting a mask when the user cancels

        :test_condition: image.export_mask() is not called

        :param setup: The setup fixture
        :returns: None
        """
        controller = Controller(MagicMock())
        controller.current_patch = 5

        tkinter.filedialog.askdirectory = MagicMock(return_value=None)

        mocker.patch('friendly_ground_truth.model.model.Image.__init__',
                     return_value=None)

        mock_image = MagicMock()

        controller.image = mock_image
        controller.image_path = '/this/is/a/path.png'
        controller.save_mask()

        mock_image.export_mask.assert_not_called()

    def test_save_mask_except(self, setup, mocker):
        """
        Test saving a mask when the image.export_mask() function raises an
        IOError


        :param setup: The setup fixture
        :returns: None
        """

        def raise_IOError(self):
            raise IOError

        controller = Controller(MagicMock())
        controller.current_patch = 5

        # fd = file_dialog_patch.return_value.__enter__.return_value

        # fd.GetPath.return_value = 'fake/path/test.png'

        mock_image = MagicMock()
        mock_image.export_mask.side_effect = raise_IOError

        controller.image = mock_image

        controller.image_path = '/this/is/a/path.png'

        controller.save_mask()

        # mock_LogError.assert_called()

    def test_display_current_patch(self, setup, mocker):
        """
        Test displaying the current patch

        :test_condition: main_window.show_image is called with the current
                         patch's overlay image

        :param setup: A setup fixture
        :param mocker: Mocker
        :returns: None
        """
        controller = Controller(MagicMock())
        controller.current_patch = 0

        mock_image = MagicMock()
        mock_patch = MagicMock()

        mock_patch.overlay_image.return_value = 1
        mock_image.patches.return_value = [mock_patch]

        controller.image = mock_image

        mock_window = MagicMock()

        controller.main_window = mock_window

        controller.display_current_patch()

        mock_window.show_image.assert_called()
        mock_window.show_image.assert_called_with(mock_image.
                                                  patches[0].overlay_image)

    def test_handle_zoom_positive(self, setup, mocker):
        """
        Test when the zoom function is called and the wheel rotaion is positive

        :test_condition:  main_window.image_scale is multiplied by 2

        :param setup: Setup
        :param mocker: Mocker
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.main_window = MagicMock()
        controller.main_window.image_scale = 1
        controller.main_window.MAX_SCALE = 16
        controller.main_window.MIN_SCALE = 0.25

        controller.image = MagicMock()

        old_scale = controller.main_window.image_scale

        result = controller.handle_zoom(1, 10, 10)

        assert controller.main_window.image_scale != old_scale
        computed_old_scale = (controller.main_window.image_scale /
                              controller.ZOOM_SCALE)
        assert computed_old_scale == old_scale
        assert True is result

    def test_handle_zoom_negative(self, setup, mocker):
        """
        Test when the zoom function is called and the wheel rotaion is negative

        :test_condition:  main_window.image_scale is divided by 2

        :param setup: Setup
        :param mocker: Mocker
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.main_window = MagicMock()
        controller.main_window.image_scale = 2
        controller.main_window.MAX_SCALE = 16
        controller.main_window.MIN_SCALE = 0.25
        controller.image = MagicMock()

        old_scale = controller.main_window.image_scale

        result = controller.handle_zoom(-1, 15, 15)

        assert controller.main_window.image_scale != old_scale
        computed_old_scale = (controller.main_window.image_scale *
                              controller.ZOOM_SCALE)
        assert computed_old_scale == old_scale
        assert True is result

    def test_handle_zoom_invalid(self, setup, mocker):
        """
        Test when the zoom function is called and the wheel rotation is 0
        :test_condition:  returns False

        :param setup: Setup
        :param mocker: Mocker
        :returns: None
        """

        controller = Controller(MagicMock())
        controller.main_window = MagicMock()
        controller.main_window.image_scale = 2
        controller.image = MagicMock()

        assert controller.handle_zoom(0, 32, 32) is False

    def test_adjust_remove_landmark_brush_positive_rot(self, setup):
        """
        Test when the mouse wheel has a positive rotation
        in Mode.REMOVE_LANDMARK

        :test_condition: The remove_landmark_radius is increased by 1

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())

        old_add_radius = controller.remove_landmark_radius

        controller.adjust_remove_landmark_brush(1)

        assert controller.remove_landmark_radius != old_add_radius
        assert (controller.remove_landmark_radius - 1) == old_add_radius

    def test_adjust_remove_landmark_brush_negative_rot(self, setup):
        """
        Test when the mouse wheel has a negative rotation in
        Mode.REMOVE_LANDMARK

        :test_condition: The remove_landmark_radius is decreased by 1

        :param setup: The setup fixture
        :returns: None
        """

        controller = Controller(MagicMock())

        old_add_radius = controller.remove_landmark_radius

        controller.adjust_remove_landmark_brush(-1)

        assert controller.remove_landmark_radius != old_add_radius
        assert (controller.remove_landmark_radius + 1) == old_add_radius

    def test_show_saved_preview(self, setup, mocker):
        """
        Test showing the preview

        :param setup: Setup
        :param mocker: Mocker
        :returns: None
        """

        mocker.patch('matplotlib.pyplot.imshow')
        show_patch = mocker.patch('matplotlib.pyplot.show')
        mocker.patch('skimage.io.imread')
        mocker.patch('skimage.color.label2rgb')
        mocker.patch('skimage.segmentation.mark_boundaries')

        mask = np.random.randint(2, size=(10, 10))
        rows = np.any(mask, axis=1)
        mocker.patch('numpy.any', return_value=np.any(mask, axis=1))
        mocker.patch('numpy.where', return_value=np.where(rows))
        mocker.patch('numpy.load')

        controller = Controller(MagicMock())
        controller.image_path = MagicMock()
        controller.label_pathname = MagicMock()
        controller.mask_pathname = MagicMock()

        controller.show_saved_preview()
        show_patch.assert_called()
