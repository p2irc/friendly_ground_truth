"""
File Name: friendly_ground_truth.py

Authors: Kyle Seidenthal

Date: 20-02-2020

Description: The entry point for the application

"""

from tkinter import Tk
import tkinter as tk
from PIL import ImageTk as itk
from PIL import Image
from io import BytesIO

import logging
import sys
import base64
import os
import shutil

from tkinter import messagebox

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

    if sys.platform == 'win32':

        home = os.path.expanduser("~")

        tools = os.path.join(home, "Tools")

        if os.getcwd() != tools:

            root = tk.Tk()

            def exit():
                root.destroy()

            def install():
                EXE = "./friendly_gt-windows.exe"

                if sys.platform != 'win32':
                    sys.exit(0)

                from win32com.client import Dispatch

                home = os.path.expanduser("~")

                tools = os.path.join(home, "Tools")

                if not os.path.exists(tools):
                    os.mkdir(tools)

                program_path = os.path.join(tools, 'friendly_gt-windows.exe')

                shutil.copy(EXE, program_path)

                path = "AppData\Roaming\Microsoft\Windows\Start Menu\Programs"

                path = os.path.join(home, path)

                if not os.path.exists(path):
                    messagebox.showinfo(title="Something Went Wrong",
                                        message="Sorry, there was an issue"
                                        " creating the shortcut.")
                    sys.exit(0)

                path = os.path.join(path, "Friendly Ground Truth.lnk")
                target = program_path
                wDir = tools
                icon = program_path

                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortcut(path)
                shortcut.Targetpath = target
                shortcut.WorkingDirectory = wDir
                shortcut.IconLocation = icon
                shortcut.save()

                messagebox.showinfo(title="Success!",
                                    message="Application Installed!")
                root.destroy()

            label_text = "Would you like to install a\n" +\
                         "start menu shortcut for Friendly Ground Truth?"

            label = tk.Label(root, text=label_text)

            button_panel = tk.Frame(root)

            ok_button = tk.Button(button_panel, text="Yes", command=install)
            cancel_button = tk.Button(button_panel, text="No", command=exit)

            ok_button.pack(side='right')
            cancel_button.pack(side='left')

            label.pack()
            button_panel.pack(fill='both')

            root.mainloop()

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
