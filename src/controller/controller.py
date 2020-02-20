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
