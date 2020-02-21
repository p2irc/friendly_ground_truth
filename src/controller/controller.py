"""
File Name: controller.py

Authors: Kyle Seidenthal

Date: 20-02-2020

Description: The main controller for the application

"""
import wx
import logging

from view.view import MainWindow
from model.model import Image, Patch
from enum import Enum

module_logger = logging.getLogger('friendly_gt.controller')


class Mode(Enum):
    """
    Class representing the possible modes for editing
    """
    THRESHOLD = 1
    ADD_REGION = 2
    REMOVE_REGION = 3


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

        # Set up the main window
        self.main_window = MainWindow(self)

        # Show the window
        self.main_window.Show()

        # Set up the current mode
        self.current_mode = Mode.THRESHOLD

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

            self.image = Image(pathname)

            self.current_patch = 0
            self.display_current_patch()

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

        if self.current_patch <= len(self.image.patches):
            self.current_patch += 1
            self.display_current_patch()
        else:
            self.logger.error("No More Patches")
            # TODO: Display some sort of dialogue and save the mask

    def prev_patch(self):
        """
        Decrement the current patch and display it

        :returns: None
        """

        if self.current_patch > 0:
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
        elif new_mode_id == self.main_window.ID_TOOL_ADD:
            self.current_mode = Mode.ADD_REGION
        elif new_mode_id == self.main_window.ID_TOOL_REMOVE:
            self.current_mode = Mode.REMOVE_REGION
        else:
            self.logger.error("Invalid mode change")

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
            logger.error("Invalid mouse wheel rotation")

    def adjust_threshold(self, wheel_rotation):
        """
        Adjust the current threshold of the patch mask

        :param wheel_rotation: The rotation of the mouse wheel
        :returns: None
        """

        self.logger.debug("Adjusting patch threshold")

    def adjust_add_region_brush(self, wheel_rotation):
        """
        Adjust the size of the region brush

        :param wheel_rotation: The rotation of the mouse wheel
        :returns: None
        """

        self.logger.debug("Adjusting add region brush")


    def adjust_remove_region_brush(self, wheel_rotation):
        """
        Adjust the size of the remove region brush

        :param wheel_rotation: the rotation of the mouse wheel
        :returns: None
        """

        self.logger.debug("Adjusting the remove region brush")
