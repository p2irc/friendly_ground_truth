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
import tkinter.filedialog

from tkinter import ttk
from tkinter import messagebox

FGT_INSTALL_DIR = "friendly_gt"
FGT_FOLDER = "./friendly_gt/"

HOME = os.path.expanduser("~")

TOOLS = os.path.join(HOME, "Tools")

EXE_NAME = "friendly_gt.exe"
UNINSTALLER_NAME = "friendly_gt_uninstaller.exe"

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


class InstallDialog(tk.Frame):

    def __init__(self, master):
        super().__init__()
        tk.Frame.__init__(self, master=None)
        self.master = master
        self.master.geometry("+700+400")

        label_text = "Please choose an installation directory:"

        label = tk.Label(root, text=label_text)

        entry_panel = tk.Frame(root, pady=20)

        entry_label = tk.Label(entry_panel, text="Install Directory: ")
        entry_label.grid(row=0, column=0)

        self.out_dir = TOOLS

        self.dir_label = tk.Label(entry_panel, text=self.out_dir,
                                  borderwidth=1, relief="solid")
        self.dir_label.grid(row=0, column=3)

        dir_entry_button = tk.Button(entry_panel, text="Select",
                                     command=self.file_dialog)

        dir_entry_button.grid(row=0, column=6)

        button_panel = tk.Frame(root)
        next_button = tk.Button(button_panel, text="Next",
                                command=self.install)
        cancel_button = tk.Button(button_panel, text="Cancel",
                                  command=self.exit)

        next_button.pack(side='right')
        cancel_button.pack(side='left')

        label.pack()
        entry_panel.pack(fill='both')
        button_panel.pack(fill='both')

    def file_dialog(self):
        dir_path = tkinter.filedialog.askdirectory(initialdir=HOME)
        self.dir_label.config(text=dir_path)
        self.out_dir = dir_path

    def install(self):
        self.run_installer(self.out_dir)

    def exit(self):
        sys.exit(0)

    def check_install_dir(self, path):

        if not os.path.exists(path):
            os.mkdir(path)

        install_dir = os.path.join(path, FGT_INSTALL_DIR)

        return install_dir

    def copy_install_files(self, install_dir):
        if not os.path.exists(install_dir):
            os.mkdir(install_dir)

        self.start_progressbar(len(os.listdir(FGT_FOLDER)))
        for item in os.listdir(FGT_FOLDER):
            s = os.path.join(FGT_FOLDER, item)
            d = os.path.join(install_dir, item)

            if os.path.isdir(s):
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)

            self.update_progress_bar()

    def get_exe_path(self, install_dir):

        return os.path.join(install_dir, EXE_NAME)

    def make_shortcut(self, name, shortcut_path, exe_path, working_dir, icon):

        from win32com.client import Dispatch

        if not os.path.exists(shortcut_path):
            messagebox.showinfo(title="Something Went Wrong", message="Sorry, "
                                "there was an issue creating the shortcut.")
            sys.exit(0)

        shortcut_link = os.path.join(shortcut_path, name + ".lnk")

        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortcut(shortcut_link)
        shortcut.Targetpath = exe_path
        shortcut.WorkingDirectory = working_dir
        shortcut.IconLocation = icon
        shortcut.save()

    def run_installer(self, path):
        if sys.platform != 'win32':
            sys.exit(1)

        install_dir = self.check_install_dir(path)

        self.copy_install_files(install_dir)

        program_path = self.get_exe_path(install_dir)
        self.make_shortcut(LINK_NAME, START_MENU_PATH, program_path,
                           install_dir, program_path)

        uninstaller_path = os.path.join(install_dir, UNINSTALLER_NAME)

        self.make_shortcut("friendly_gt_unsintaller.lnk", START_MENU_PATH,
                           uninstaller_path, install_dir, program_path)

        shortcut = tk.messagebox.askyesno(title="Create Desktop Shortcut?",
                                          message="Would you like to create a"
                                          "desktop shortcut?")

        # Ask about desktop shortcut
        if shortcut:
            self.make_shortcut(LINK_NAME, DESKTOP_PATH, program_path,
                               install_dir, program_path)

        messagebox.showinfo(title="Success!", message="Application Installed!")

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

dialog = InstallDialog(root)

root.mainloop()
