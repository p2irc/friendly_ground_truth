"""
File Name: friendly_ground_truth.py

Authors: Kyle Seidenthal

Date: 20-02-2020

Description: The entry point for the application

"""

import wx
import logging
from controller.controller import Controller

logger = logging.getLogger('friendly_gt')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter and add it to the handlers
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(log_format)
ch.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(ch)


if __name__ == '__main__':
    app = wx.App(False)

    controller = Controller()

    logger.debug('Main application window is running')
    app.MainLoop()
