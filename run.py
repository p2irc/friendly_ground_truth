"""
File Name: friendly_ground_truth.py

Authors: Kyle Seidenthal

Date: 20-02-2020

Description: The entry point for the application

"""

from tkinter import Tk
import logging
import sys

from friendly_ground_truth.controller.controller import Controller

debug = False

if len(sys.argv) > 1:

    arg = sys.argv[1]

    if arg == '-debug':
        debug = True


logger = logging.getLogger('friendly_gt')

if debug:
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
    root = Tk()
    root.attributes('-zoomed', True)
    controller = Controller(root)

    logger.debug('Main application window is running')
    root.mainloop()
