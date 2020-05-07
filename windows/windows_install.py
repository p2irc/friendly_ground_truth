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
import requests

from tkinter import messagebox


def exit():
    sys.exit(0)

def copytree(src, dst, symlinks=False, ignore=None):
     for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def install():
    folder = "./friendly_gt"
    EXE = "./friendly_gt/friendly_gt.exe"

    if sys.platform != 'win32':
        sys.exit(0)

    from win32com.client import Dispatch

    home = os.path.expanduser("~")

    tools = os.path.join(home, "Tools")

    if not os.path.exists(tools):
        os.mkdir(tools)


    copytree(folder, tools)

    program_path = os.path.join(tools, "friendly_gt", "friendly_gt.exe")
    path = "AppData\Roaming\Microsoft\Windows\Start Menu\Programs"

    path = os.path.join(home, path)

    if not os.path.exists(path):
        messagebox.showinfo(title="Something Went Wrong", message="Sorry, "
                            "there was an issue creating the shortcut.")
        sys.exit(0)

    path = os.path.join(path, "Friendly Ground Truth.lnk")
    target = os.path.join(tools, "friendly_gt", "friendly_gt.exe")
    wDir = tools
    icon = program_path

    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortcut(path)
    shortcut.Targetpath = target
    shortcut.WorkingDirectory = wDir
    shortcut.IconLocation = icon
    shortcut.save()

    messagebox.showinfo(title="Success!", message="Application Installed!")

    sys.exit(0)


root = tk.Tk()

label_text = "Would you like to install Friendly Ground Truth?"

label = tk.Label(root, text=label_text)

button_panel = tk.Frame(root)

ok_button = tk.Button(button_panel, text="Yes", command=install)
cancel_button = tk.Button(button_panel, text="No", command=exit)

ok_button.pack(side='right')
cancel_button.pack(side='left')

label.pack()
button_panel.pack(fill='both')

root.mainloop()


