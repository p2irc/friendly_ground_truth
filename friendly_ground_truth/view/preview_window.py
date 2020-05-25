"""
File Name: preview_window.py

Authors: Kyle Seidenthal

Date: 18-05-2020

Description: An image mask preview window.

"""

import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk as itk


class PreviewWindow(tk.Toplevel):
    """
    A window for previewing an image.

    Attributes:
        img: The image for previewing
    """

    def __init__(self, img, controller, style):
        self._base = tk.Toplevel()
        self._base.title("Preview")

        self._frame = ttk.Frame(self._base)

        self._canvas_size = img.shape[0]//2, img.shape[1]//2

        self._base.minsize(width=self._canvas_size[1] + 50,
                           height=self._canvas_size[0] + 50)
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

        self._button_panel.pack(side='top', fill='both')

        self._canvas = tk.Canvas(self._frame)

        background = style.lookup("Canvas.TFrame", "background")
        self._canvas.config(background=background)

        self._canvas.pack(fill='both', expand='yes')
        self._frame.pack(fill='both', expand=True)
        self._show_image()

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

    def _show_image(self):
        """
        Display the image on the canvas.


        Returns:
            None

        Postconditions:
            The image is displayed on the canvas.
        """
        image = Image.fromarray(self.img)

        canvas_h = self._canvas_size[0]
        canvas_w = self._canvas_size[1]

        size = (canvas_w, canvas_h)
        image = image.resize(size)
        self._display_img = itk.PhotoImage(image=image)

        x, y = 0, 0  # self.image_x, self.image_y

        self._image_id = self._canvas.create_image(x, y, anchor="nw",
                                                   image=self._display_img)
        self._canvas.image = self._display_img
        self._canvas.pack()
