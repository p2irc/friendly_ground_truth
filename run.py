"""
File Name: friendly_ground_truth.py

Authors: Kyle Seidenthal

Date: 20-02-2020

Description: The entry point for the application

"""

from tkinter import Tk
from PIL import ImageTk as itk
from PIL import Image
from io import BytesIO

import logging
import sys
import base64


from friendly_ground_truth.controller.controller import Controller
from friendly_ground_truth.view.icons.icon_strings import fgt_favicon

debug = False
show_events = False

if len(sys.argv) > 1:

    for arg in sys.argv:
        if arg == '-debug':
            debug = True

        if arg == '-events':
            show_events = True

logger = logging.getLogger('friendly_gt')

event_logger = logging.getLogger('event_logger')
event_logger.setLevel(logging.INFO)

if debug:
    logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

fh = logging.FileHandler('events.log')
fh.setLevel(logging.INFO)

# create formatter and add it to the handlers
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(log_format)
ch.setFormatter(formatter)

event_format = '%(message)s'
event_formatter = logging.Formatter(event_format)
fh.setFormatter(event_formatter)

# add the handlers to the logger
logger.addHandler(ch)
event_logger.addHandler(fh)


if show_events:
    event_logger_handler = logging.StreamHandler()
    event_logger_handler.setLevel(logging.INFO)
    event_logger_handler.setFormatter(event_formatter)
    event_logger.addHandler(event_logger_handler)


if __name__ == '__main__':

    icon_data = base64.b64decode(fgt_favicon)
    icon_data = Image.open(BytesIO(icon_data))

    root = Tk()

    img = itk.PhotoImage(icon_data)

    root.wm_iconphoto(True, img)

    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry("%dx%d+0+0" % (w, h))

    controller = Controller(root)

    logger.debug('Main application window is running')
    root.mainloop()
