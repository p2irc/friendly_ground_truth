"""
File Name: controller.py

Authors: Kyle Seidenthal

Date: 20-02-2020

Description: The main controller for the application

"""
import wx
import logging
import os

from friendly_ground_truth.view.view import MainWindow
from friendly_ground_truth.model.model import Image
from enum import Enum

module_logger = logging.getLogger('friendly_gt.controller')


class Mode(Enum):
    """
    Class representing the possible modes for editing
    """
    THRESHOLD = 1
    ADD_REGION = 2
    REMOVE_REGION = 3
    NO_ROOT = 4


class Controller:
    """
    The main controller object for the application
    """

    def __init__(self):
        """
        Initialize the controller module

        :returns: None
        """
        self.logger = logging.getLogger('friendly_gt.controller.Controller')
        self.logger.debug("Creating controller instance")

        self.current_patch = 0

        # Set up the current mode
        self.current_mode = Mode.THRESHOLD

        # Brush radii
        self.add_region_radius = 15
        self.remove_region_radius = 15

        # Set up the main window
        self.main_window = MainWindow(self)

        # Show the window
        self.main_window.Show()

    def load_new_image(self):
        """
        Called when the user wants to load a new image to open a file
        browser dialogue and get the image path

        :returns: None
        """
        self.logger.debug("Opening load file dialog")

        with wx.FileDialog(self.main_window, "Open an image",
                           wildcard="PNG and TIFF files (*.png; *.tiff)\
                                    |*.png;*.tiff|TIF files (*.tif)|*.tif",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
                           ) as file_dialog:

            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Proceed loading the file chosen by the user
            pathname = file_dialog.GetPath()
            self.logger.debug("File Path: %s", pathname)
            self.image_path = pathname

            try:
                self.image = Image(pathname)
            except FileNotFoundError:
                self.logger.debug("There was a problem loading the image")
                # TODO: Display an error dialog
                return

            self.current_patch = 0
            self.display_current_patch()

    def get_image_name_from_path(self, path):
        """
        Get the filename from the image to use for saving the mask

        :param path: The path to the original image
        :returns: The new filename for the mask
        """

        if os.path.isdir(path):
            raise ValueError("Cannot get image name from a directory.")

        basename = os.path.basename(path)
        return os.path.splitext(basename)[0] + '_mask.png'

    def save_mask(self):
        """
        Save the finished image mask

        :returns: None
        """

        with wx.DirDialog(self.main_window, "Select Output Folder",
                          style=wx.DD_DEFAULT_STYLE
                          ) as file_dialog:

            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # save the current contents in the file
            pathname = file_dialog.GetPath()
            image_name = self.get_image_name_from_path(self.image_path)

            pathname = os.path.join(pathname, image_name)

            try:
                self.logger.debug("Saving mask to {}".format(pathname))
                self.image.export_mask(pathname)
            except IOError:
                wx.LogError("Cannot save file '%s'." % pathname)
                # TODO: display dialog

    def display_current_patch(self):
        """
        Display the current patch to be displayed

        :returns: None
        """

        patch = self.image.patches[self.current_patch]

        self.main_window.show_image(patch.overlay_image)

    def next_patch(self):
        """
        Increment the current patch and display it

        :returns: None
        """

        if self.current_patch < len(self.image.patches)-1:
            self.current_patch += 1
            while self.image.patches[self.current_patch].display is False:
                self.current_patch += 1
            self.display_current_patch()
        else:
            self.logger.error("No More Patches")

            dialog_message = "No More Patches - Would you like to save the" \
                             " mask?"

            dialog_title = "No More Patches"

            dialog = wx.MessageDialog(None, dialog_message, dialog_title,
                                      wx.YES_NO | wx.ICON_QUESTION |
                                      wx.NO_DEFAULT)

            if dialog.ShowModal() == wx.ID_YES:
                self.save_mask()

    def prev_patch(self):
        """
        Decrement the current patch and display it

        :returns: None
        """

        if self.current_patch > 0:
            self.current_patch -= 1
            while self.image.patches[self.current_patch].display is False:
                self.current_patch -= 1

            self.display_current_patch()

        else:
            self.logger.error("No Previous patches")

    def change_mode(self, new_mode_id):
        """
        Change the current editing mode

        :param new_mode_id: The ID of the mode button in the Main Window
        :returns: None
        """

        if new_mode_id == self.main_window.ID_TOOL_THRESH:
            self.current_mode = Mode.THRESHOLD
            self.main_window.set_brush_radius(0)

        elif new_mode_id == self.main_window.ID_TOOL_ADD:
            self.current_mode = Mode.ADD_REGION
            self.main_window.set_brush_radius(self.add_region_radius)

        elif new_mode_id == self.main_window.ID_TOOL_REMOVE:
            self.current_mode = Mode.REMOVE_REGION
            self.main_window.set_brush_radius(self.remove_region_radius)

        elif new_mode_id == self.main_window.ID_TOOL_NO_ROOT:
            self.no_root_activate()
        else:
            self.logger.error("Invalid mode change")

    def no_root_activate(self):
        """
        Set the mask for the patch to zero, there is no root here

        :returns: None
        """

        patch = self.image.patches[self.current_patch]
        patch.clear_mask()
        patch.overlay_mask()

        self.display_current_patch()

    def handle_mouse_wheel(self, wheel_rotation):
        """
        Handle wheel rotation coming from the mouse

        :param wheel_rotation: The wheel rotation
        :returns: None
        """

        if self.current_mode == Mode.THRESHOLD:

            self.adjust_threshold(wheel_rotation)

        elif self.current_mode == Mode.ADD_REGION:
            self.adjust_add_region_brush(wheel_rotation)

        elif self.current_mode == Mode.REMOVE_REGION:
            self.adjust_remove_region_brush(wheel_rotation)

        else:
            self.logger.error("Invalid mouse wheel rotation")
            return False

    def handle_left_click(self, click_location):
        """
        Handle a left mouse click at the given location

        :param click_location: The location (x, y) of the click
        :returns: None
        """

        if self.current_mode == Mode.ADD_REGION:
            self.logger.debug("Add region click")
            patch = self.image.patches[self.current_patch]
            patch.add_region(click_location, self.add_region_radius)
            self.display_current_patch()

        elif self.current_mode == Mode.REMOVE_REGION:
            self.logger.debug("Remove region click")
            patch = self.image.patches[self.current_patch]
            patch.remove_region(click_location, self.remove_region_radius)
            self.display_current_patch()

        else:
            return False

    def handle_left_release(self):
        """
        Handle the release of the left mouse button

        :returns: None
        """

        if self.current_mode == Mode.ADD_REGION:
            self.logger.debug("Add region release")
            return True

        elif self.current_mode == Mode.REMOVE_REGION:
            self.logger.debug("Remove region release")
            return True

        else:
            return False

    def handle_motion(self, position):
        """
        Handle motion events of the mouse at the given position

        :param position: The position (x, y) of the mouse during the event
        :returns: None
        """

        if self.current_mode == Mode.ADD_REGION:
            self.logger.debug("Adding region")
            patch = self.image.patches[self.current_patch]
            patch.add_region(position, self.add_region_radius)
            self.display_current_patch()

        elif self.current_mode == Mode.REMOVE_REGION:
            self.logger.debug("Removing Region")

            patch = self.image.patches[self.current_patch]
            patch.remove_region(position, self.remove_region_radius)
            self.display_current_patch()

        else:
            return False

    def adjust_threshold(self, wheel_rotation):
        """
        Adjust the current threshold of the patch mask

        :param wheel_rotation: The rotation of the mouse wheel
        :returns: None
        """

        self.logger.debug("Adjusting patch threshold")

        patch = self.image.patches[self.current_patch]

        # Adjust the threshold.  Note that it is inverted, because it feels
        # more natural to scroll down to 'reduce' the region, rather than
        # reducing the threshold
        if wheel_rotation > 0 and patch.thresh > 0:
            patch.thresh -= 0.01

        elif wheel_rotation < 0 and patch.thresh < 1:
            patch.thresh += 0.01

        patch.apply_threshold(patch.thresh)
        patch.overlay_mask()

        self.logger.debug("Threshold value: {}".format(patch.thresh))
        self.display_current_patch()

    def adjust_add_region_brush(self, wheel_rotation):
        """
        Adjust the size of the region brush

        :param wheel_rotation: The rotation of the mouse wheel
        :returns: None
        """

        self.logger.debug("Adjusting add region brush")
        if wheel_rotation > 0:
            self.add_region_radius += 1
        else:
            self.add_region_radius -= 1

        self.main_window.set_brush_radius(self.add_region_radius)
        self.main_window.draw_brush()

    def adjust_remove_region_brush(self, wheel_rotation):
        """
        Adjust the size of the remove region brush

        :param wheel_rotation: the rotation of the mouse wheel
        :returns: None
        """

        self.logger.debug("Adjusting the remove region brush")
        if wheel_rotation > 0:
            self.remove_region_radius += 1
        else:
            self.remove_region_radius -= 1

        self.main_window.set_brush_radius(self.remove_region_radius)
        self.main_window.draw_brush()
