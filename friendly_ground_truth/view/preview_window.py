"""
File Name: preview_window.py

Authors: Kyle Seidenthal

Date: 18-05-2020

Description: An image mask preview window.

"""

import tkinter as tk
from tkinter import ttk

from friendly_ground_truth.view.fgt_canvas import PatchNavCanvas


class PreviewFrame(ttk.Frame):

    def __init__(self, master, img, controller, style):

        ttk.Frame.__init__(self, master=master, style="Preview.TFrame")

        self._master = master

        self.img = img
        self.controller = controller

        self._banner = ttk.Frame(self, borderwidth=5,
                                 style="ButtonPanel.TFrame")

        self._banner_label = ttk.Label(self._banner, text="Preview")

        self._banner_label.pack(side="left")

        self._roi_button = ttk.Button(self._banner, text="ROI",
                                      command=self._on_roi,
                                      style="Preview.TButton")

        self._roi_button.pack(side="right")

        self._canvas = PatchNavCanvas(self, self.img, self, style)

        self._canvas.set_zoom(-5)

        self._banner.grid(row=0, column=0, sticky="NEW")
        self._canvas.grid(row=1, column=0, sticky="NSEW")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

    def set_theme(self, style):

        self._canvas.set_theme(style)

    def navigate_to_patch(self, pos):
        """
        Navigate to the patch containing the given coordinates in the original
        image.

        Args:
            pos: The position in the image to go to.

        Returns:
            None
        """

        self.controller.navigate_to_patch(pos)

    def update_image(self, img):
        """
        Update the preview image.

        Args:
            img: The image to show in the preview.

        Returns:
            None
        """
        self.img = img
        self._canvas.set_image(self.img)

    def new_image(self, img):
        """
        Reset the image on the canvas.

        Args:
            img: The image.

        Returns:
            None
        """
        self.img = img
        self._canvas.new_image(img)

    def _on_roi(self):
        self._canvas.activate_roi()
        self._roi_button.state(['disabled'])

    def stop_roi(self, start, end):
        self._roi_button.state(['!disabled'])

        self.controller.select_roi(start, end)


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

        self._frame = PreviewFrame(self._base, img, controller, style)

        self._frame.pack(fill='both', expand=True)

    def update_image(self, img):
        """
        Update the preview image.

        Args:
            img: The image to display.

        Returns:
            None.
        """

        self._frame.update_image(img)

    def set_theme(self, style):

        self._frame.set_theme(style)

    def destroy(self):

        self._base.destroy()
