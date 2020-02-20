"""
File Name: controller.py

Authors: Kyle Seidenthal

Date: 20-02-2020

Description: The main controller for the application

"""
import wx
import logging

from view.view import MainWindow

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

        # TODO: initilize the model eg) self.model = Model()

        # Set up the main window
        self.main_window = MainWindow()

        # Show the window
        self.main_window.Show()

    # TODO: add controlling functions that manipulate the model here
