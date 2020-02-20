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

module_logger = logging.getLogger('friendly_gt.controller')


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


