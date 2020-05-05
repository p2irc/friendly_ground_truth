"""
File Name: windows_install.py

Authors: Kyle Seidenthal

Date: 05-05-2020

Description: Moves the executable to a suitable directory on windows

"""

import os
import shutil
import sys
import tkinter as tk
from tkinter import messagebox


def exit():
    sys.exit(0)

def install():
    EXE = "./friendly_gt.exe"

    if sys.platform != 'win32':
        sys.exit(0)

    from win32com.client import Dispatch

    home = os.expanduser("~")

    tools = os.path.join(home, "Tools")

    if not os.path.exists(tools):
        os.mkdir(tools)

    program_path = os.path.join(tools, 'friendly_gt.exe')

    shutil.copy(EXE, program_path)

    path = "%appdata%\Microsoft\Windows\Start Menu\Programs\Friendly Ground Truth.lnk"

    path = os.path.join(home, path)

    if not os.path.exists(path):
        messagebox.showinfo(title="Something Went Wrong", message="Sorry, "
                            "there was an issue creating the shortcut.")
        sys.exit(0)

    target = program_path
    wDir = tools
    icon = program_path

    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortcut(path)
    shortcut.Targetpath = target
    shortcut.WorkingDirectory = wDir
    shortcut.IconLocation = icon
    shortcut.save()

    messagebox.showinfo(title="Success!", message="Application Installed!")

root = tk.Tk()

label_text = "Would you like to install a\n start menu shortcut for Friendly Ground Truth?"

label = tk.Label(root, text=label_text)

button_panel = tk.Frame(root)

ok_button = tk.Button(button_panel, text="Yes", command=install)
cancel_button = tk.Button(button_panel, text="Cancel", command=exit)

ok_button.pack(side='right')
cancel_button.pack(side='left')

label.pack()
button_panel.pack(fill='both')

root.mainloop()


