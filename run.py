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
