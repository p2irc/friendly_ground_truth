"""
File Name: windows_install.py

Authors: Kyle Seidenthal

Date: 05-05-2020

Description: Removes all traces of the program on windows

"""

import os
import sys
import tkinter as tk
import tkinter.filedialog

from tkinter import ttk
from tkinter import messagebox

FGT_INSTALL_DIR = "friendly_gt"
FGT_FOLDER = "./friendly_gt/"

HOME = os.path.expanduser("~")

TOOLS = os.path.join(HOME, "Tools")

EXE_NAME = "friendly_gt.exe"

START_MENU = r"AppData\Roaming\Microsoft\Windows\Start Menu\Programs"
START_MENU_PATH = os.path.join(HOME, START_MENU)

if sys.platform == 'win32':
    from win32com.shell import shell, shellcon

    try:
        desktop = shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOP, 0, 0)

        if not os.path.exists(desktop):
            DESKTOP_PATH = os.path.join(HOME, "Desktop")
        else:
            DESKTOP_PATH = desktop
    except Exception:
        print("Could not get system desktop folder")
        DESKTOP_PATH = os.path.join(HOME, "Desktop")

LINK_NAME = "Friendly Ground Truth"


class UnInstallDialog(tk.Frame):

    def __init__(self, master):
        super().__init__()
        tk.Frame.__init__(self, master=None)
        self.master = master
        self.master.geometry("+700+400")

        label_text = "Are you sure you want to uninstall"\
                     " Friendly Ground Truth?"

        label = tk.Label(root, text=label_text)

        self.install_dir = os.getcwd()

        button_panel = tk.Frame(root)
        next_button = tk.Button(button_panel, text="Yes",
                                command=self.uninstall)
        cancel_button = tk.Button(button_panel, text="Cancel",
                                  command=self.exit)

        next_button.pack(side='right')
        cancel_button.pack(side='left')

        label.pack()
        button_panel.pack(fill='both')

    def uninstall(self):
        self.run_uninstaller(self.install_dir)

    def exit(self):
        sys.exit(0)

    def remove_install_files(self, install_dir):
        if not os.path.exists(install_dir):
            return

        if FGT_INSTALL_DIR not in install_dir:
            print(FGT_INSTALL_DIR + " not found. Aborting.")
            return

        self.start_progressbar(len(os.listdir(install_dir)))
        for item in os.listdir(install_dir):
            d = os.path.join(install_dir, item)

            try:
                os.remove(d)
            except OSError as e:
                print(e)

            self.update_progress_bar()

    def get_exe_path(self, install_dir):

        return os.path.join(install_dir, EXE_NAME)

    def run_uninstaller(self, path):
        if sys.platform != 'win32':
            sys.exit(1)

        self.remove_install_files(self.install_dir)

        shortcut_path = os.path.join(START_MENU_PATH, LINK_NAME)

        try:
            os.remove(shortcut_path)
        except OSError as e:
            print("Could not remove start menu shortcut: " + e)

        desktop_shortcut = os.path.join(DESKTOP_PATH, LINK_NAME)

        try:
            os.remove(desktop_shortcut)
        except OSError as e:
            print("Could not remove desktop shortcut: " + e)

        messagebox.showinfo(title="Success!",
                            message="Application Uninstalled!")

        sys.exit(0)

    def start_progressbar(self, num_items):
        """
        Start displaying a progressbar

        :returns: None
        """
        self.prog_popup = tk.Toplevel()
        self.num_files = num_items
        self.prog_popup.geometry("100x50+500+400")

        tk.Label(self.prog_popup, text="Installing").grid(row=0, column=0)

        self.load_progress = 0
        self.load_prog_var = tk.DoubleVar()
        self.load_prog_bar = ttk.Progressbar(self.prog_popup,
                                             variable=self.load_prog_var,
                                             maximum=100)
        self.load_prog_bar.grid(row=1, column=0)

        self.progress_step = float(100.0/num_items)
        self.prog_popup.pack_slaves()

    def update_progress_bar(self):
        """
        Update the progress bar popup

        :returns: None
        """

        self.prog_popup.update()
        self.load_progress += self.progress_step
        self.load_prog_var.set(self.load_progress)

        if self.load_progress >= self.num_files:
            self.prog_popup.destroy()


root = tk.Tk()

dialog = UnInstallDialog(root)

root.mainloop()
