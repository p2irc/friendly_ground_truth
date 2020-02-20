"""
File Name: view.py

Authors: Kyle Seidenthal

Date: 20-02-2020

Description: Classes that represent the view for the application

"""

import wx
import logging

module_logger = logging.getLogger('friendly_gt.view')

class MainWindow(wx.Frame):
    """
    The main window for displaying image patches and such
    """

    def __init__(self, parent=None):
        """
        Initializes the main window

        :param parent: The parent frame for this frame  The default value is None.
        :returns: None
        """
        self.logger = logging.getLogger('friendly_gt.view.MainWindow')
        wx.Frame.__init__(self, parent, -1, "Main Window")
        self.logger.debug("Window created successfully")
