"""
File Name: preview_window.py

Authors: Kyle Seidenthal

Date: 18-05-2020

Description: An image mask preview window.

"""

import tkinter as tk
from tkinter import ttk

from friendly_ground_truth.view.fgt_canvas import ScrollableImageCanvas


class PreviewWindow(tk.Toplevel):
    """
    A window for previewing an image.

    Attributes:
        img: The image for previewing
    """

    def __init__(self, img, controller, style):
        self._base = tk.Toplevel()
        self._base.title("Preview")
        self._base.geometry("1000x800+200+200")

        self._frame = ttk.Frame(self._base)

        self.img = img
        self.controller = controller

        self._button_panel = ttk.Frame(self._frame, borderwidth=5,
                                       style="ButtonPanel.TFrame")

        self._save_button = ttk.Button(self._button_panel, text="Save",
                                       command=self._on_save)

        self._save_button.pack(side='right')

        self._cancel_button = ttk.Button(self._button_panel, text="Cancel",
                                         command=self._on_cancel)

        self._cancel_button.pack(side='left')

        self._button_panel.grid(row=0, column=0, sticky="NEW")
        self._canvas = ScrollableImageCanvas(self._frame, self.img, self,
                                             style)

        self._canvas.set_zoom(-5)

        self._canvas.grid(row=1, column=0, sticky="NSEW")
        self._frame.grid_columnconfigure(0, weight=1)
        self._frame.grid_rowconfigure(0, weight=0)
        self._frame.grid_rowconfigure(1, weight=1)

        self._frame.pack(fill='both', expand=True)

    def _on_save(self):
        """
        Called when the save button is pressed.


        Returns:
            None

        Postconditions:
            The mask is saved and the window is destroyed.
        """
        self._base.withdraw()
        self.controller.save_mask()
        self._base.destroy()

    def _on_cancel(self):
        """
        Called when the cancel button is pressed.


        Returns:
            None

        Postconditions:
            The window is destroyed.
        """
        self._base.destroy()
