"""
File Name: tk_view.py

Authors: Kyle Seidenthal

Date: 06-04-2020

Description: Tkinter Version of the GUI

"""

import tkinter as tk
import os

from tkinter import LEFT, TOP, X, FLAT, RAISED, SUNKEN
from tkinter import Frame

from PIL import Image, ImageTk
from sys import platform

import logging
module_logger = logging.getLogger('friendly_gt.view')

ICON_PATH = "friendly_ground_truth/view/icons/1x"


class MainWindow(Frame):

    # Constant button IDs
    ID_TOOL_THRESH = 101
    ID_TOOL_ADD = 102
    ID_TOOL_REMOVE = 103
    ID_TOOL_NO_ROOT = 104
    ID_TOOL_PREV_IMAGE = 105
    ID_TOOL_NEXT_IMAGE = 106
    ID_TOOL_ZOOM = 107
    ID_TOOL_FLOOD_ADD = 108
    ID_TOOL_FLOOD_REMOVE = 109

    def __init__(self, controller, master):

        super().__init__()
        Frame.__init__(self, master=None)

        self.master = master
        self.controller = controller

        master.geometry("250x150+300+300")
        master.title("Friendly Ground Truth")
        # Initialize the logger
        self.logger = logging.getLogger('friendly_gt.view.MainWindow')

        self.create_menubar()

        self.create_canvas()

        self.set_up_interactions()

    def set_up_interactions(self):
        """
        Set up user interactions with keyboard and mouse

        :returns: None
        """

        # Apparently bindings are different fro different OSes
        if platform == "linux" or platform == "linux2":
            self.bind_all("<Button-4>", self.on_mousewheel)
            self.bind_all("<Button-5>", self.on_mousewheel)
        # Mac
        elif platform == "darwin":
            self.bind_all("<MouseWheel>", self.on_mousewheel)

        elif platform == "win32":
            self.bind_all("<MouseWheel>", self.on_mousewheel)

    def create_canvas(self):
        """
        Set up a canvas for displaying images

        :returns: None
        """

        self.canvas = tk.Canvas(self, cursor="cross", width=1000, height=1000)

    def create_menubar(self):
        """
        Create the menu bar

        :returns: None
        """

        self.menubar = tk.Menu(self.master)

        self.create_file_menu()

        self.create_toolbar()

        self.master.config(menu=self.menubar)

    def create_file_menu(self):
        """
        Create the file menu bar

        :returns: None
        """

        self.filemenu = tk.Menu(self.menubar, tearoff=0)

        self.filemenu.add_command(label="Load Image",
                                  command=self.on_load_image)

        self.filemenu.add_command(label="Save Mask", command=self.on_save_mask)

        self.menubar.add_cascade(label="File", menu=self.filemenu)

    def create_toolbar(self):
        """
        Create the toolbar

        :returns: None
        """

        self.toolbar = tk.Frame(self.master, bd=1, relief=RAISED)
        self.toolbar_buttons = {}

        # Threshold Button
        thresh_icon_path = os.path.join(ICON_PATH,
                                        "baseline_tune_black_18dp.png")
        thresh_img = Image.open(thresh_icon_path)
        thresh_icon = ImageTk.PhotoImage(thresh_img)

        thresh_button = tk.Button(self.toolbar, image=thresh_icon,
                                  relief=FLAT, command=self.on_threshold_tool)
        thresh_button.image = thresh_icon
        thresh_button.pack(side=LEFT, padx=2, pady=2)

        # Add Region Button
        add_reg_icon_path = os.path.join(ICON_PATH,
                                         "baseline_add_circle_outline_" +
                                         "black_18dp.png")
        add_reg_img = Image.open(add_reg_icon_path)
        add_reg_icon = ImageTk.PhotoImage(add_reg_img)

        add_reg_button = tk.Button(self.toolbar, image=add_reg_icon,
                                   relief=FLAT, command=self.on_add_reg_tool)
        add_reg_button.image = add_reg_icon
        add_reg_button.pack(side=LEFT, padx=2, pady=2)

        # Remove Region Button
        remove_reg_icon_path = os.path.join(ICON_PATH,
                                            "baseline_remove_circle_outline_" +
                                            "black_18dp.png")
        remove_reg_img = Image.open(remove_reg_icon_path)
        remove_reg_icon = ImageTk.PhotoImage(remove_reg_img)

        remove_reg_button = tk.Button(self.toolbar, image=remove_reg_icon,
                                      relief=FLAT,
                                      command=self.on_remove_reg_tool)
        remove_reg_button.image = remove_reg_icon
        remove_reg_button.pack(side=LEFT, padx=2, pady=2)

        # Zoom  Button
        zoom_icon_path = os.path.join(ICON_PATH,
                                      "baseline_zoom_in_black_18dp.png")
        zoom_img = Image.open(zoom_icon_path)
        zoom_icon = ImageTk.PhotoImage(zoom_img)

        zoom_button = tk.Button(self.toolbar, image=zoom_icon,
                                relief=FLAT, command=self.on_zoom_tool)
        zoom_button.image = zoom_icon
        zoom_button.pack(side=LEFT, padx=2, pady=2)

        # Flood Add Button
        flood_add_icon_path = os.path.join(ICON_PATH,
                                           "sharp_gps_fixed_black_18dp.png")
        flood_add_img = Image.open(flood_add_icon_path)
        flood_add_icon = ImageTk.PhotoImage(flood_add_img)

        flood_add_button = tk.Button(self.toolbar, image=flood_add_icon,
                                     relief=FLAT,
                                     command=self.on_flood_add_tool)
        flood_add_button.image = flood_add_icon
        flood_add_button.pack(side=LEFT, padx=2, pady=2)

        # Flood Remove Button
        flood_remove_icon_path = os.path.join(ICON_PATH,
                                              "sharp_gps_not_fixed_black" +
                                              "_18dp.png")
        flood_remove_img = Image.open(flood_remove_icon_path)
        flood_remove_icon = ImageTk.PhotoImage(flood_remove_img)

        flood_remove_button = tk.Button(self.toolbar, image=flood_remove_icon,
                                        relief=FLAT,
                                        command=self.on_flood_remove_tool)
        flood_remove_button.image = flood_remove_icon
        flood_remove_button.pack(side=LEFT, padx=2, pady=2)

        # No Root Button
        no_root_icon_path = os.path.join(ICON_PATH,
                                         "baseline_cancel_black_18dp.png")
        no_root_img = Image.open(no_root_icon_path)
        no_root_icon = ImageTk.PhotoImage(no_root_img)

        no_root_button = tk.Button(self.toolbar, image=no_root_icon,
                                   relief=FLAT,
                                   command=self.on_no_root_tool)
        no_root_button.image = no_root_icon
        no_root_button.pack(side=LEFT, padx=2, pady=2)

        # Prev Button
        prev_icon_path = os.path.join(ICON_PATH,
                                      "baseline_skip_previous_black_18dp.png")
        prev_img = Image.open(prev_icon_path)
        prev_icon = ImageTk.PhotoImage(prev_img)

        prev_button = tk.Button(self.toolbar, image=prev_icon,
                                relief=FLAT,
                                command=self.on_prev_tool)
        prev_button.image = prev_icon
        prev_button.pack(side=LEFT, padx=2, pady=2)

        # Next Button
        next_icon_path = os.path.join(ICON_PATH,
                                      "baseline_skip_next_black_18dp.png")
        next_img = Image.open(next_icon_path)
        next_icon = ImageTk.PhotoImage(next_img)

        next_button = tk.Button(self.toolbar, image=next_icon,
                                relief=FLAT,
                                command=self.on_next_tool)
        next_button.image = next_icon
        next_button.pack(side=LEFT, padx=2, pady=2)

        self.toolbar_buttons[self.ID_TOOL_THRESH] = thresh_button
        self.toolbar_buttons[self.ID_TOOL_ADD] = add_reg_button
        self.toolbar_buttons[self.ID_TOOL_REMOVE] = remove_reg_button
        self.toolbar_buttons[self.ID_TOOL_NO_ROOT] = no_root_button
        self.toolbar_buttons[self.ID_TOOL_PREV_IMAGE] = prev_button
        self.toolbar_buttons[self.ID_TOOL_NEXT_IMAGE] = next_button
        self.toolbar_buttons[self.ID_TOOL_ZOOM] = zoom_button
        self.toolbar_buttons[self.ID_TOOL_FLOOD_ADD] = flood_add_button
        self.toolbar_buttons[self.ID_TOOL_FLOOD_REMOVE] = flood_remove_button

        self.toolbar.pack(side=TOP, fill=X)

        self.pack()

    def on_load_image(self):
        """
        Called when the load image button is chosen

        :returns: None
        """
        self.controller.load_new_image()

    def show_image(self, img):
        """
        Display the given image in the main window

        :param img: The image to display
        :returns: None
        """

        self.current_image = img

        self.display_img = ImageTk.PhotoImage(image=Image.fromarray(img),
                                              master=self.master)

        self.canvas.create_image(0, 0, anchor="nw", image=self.display_img)
        self.canvas.pack()
        self.logger.debug("Image displayed")

    def on_save_mask(self):
        """
        Called when the save mask button is chosem

        :returns: None
        """

        # TODO: Save the mask from the controller
        pass

    def change_toolbar_state(self, new_tool_id):
        """
        Change the state of the buttons in the toolbar based on the button that
        has been chosen

        :param new_tool_id: The id of the tool that was chosen
        :returns: None
        """

        for id, button in self.toolbar_buttons.items():
            if id == new_tool_id:
                button.config(relief=SUNKEN)
            else:
                button.config(relief=RAISED)

    def on_threshold_tool(self):
        """
        Called when the threshold tool is chosen

        :returns: None
        """

        self.change_toolbar_state(self.ID_TOOL_THRESH)
        self.logger.debug("Threshold tool chosen")

        self.controller.change_mode(self.ID_TOOL_THRESH)

    def on_add_reg_tool(self):
        """
        Called when the add region brush tool is chosen

        :returns: None
        """

        self.change_toolbar_state(self.ID_TOOL_ADD)

        self.controller.change_mode(self.ID_TOOL_ADD)

    def on_remove_reg_tool(self):
        """
        Called when the remove region brush tool is chosen

        :returns: None
        """
        self.change_toolbar_state(self.ID_TOOL_REMOVE)
        self.controller.change_mode(self.ID_TOOL_REMOVE)

    def on_no_root_tool(self):
        """
        Called when the no root tool is chosen

        :returns: None
        """
        self.controller.change_mode(self.ID_TOOL_NO_ROOT)

    def on_zoom_tool(self):
        """
        Called when the zoom tool is chosen

        :returns: None
        """
        self.change_toolbar_state(self.ID_TOOL_ZOOM)
        self.controller.change_mode(self.ID_TOOL_ZOOM)

    def on_flood_add_tool(self):
        """
        Called when the flood add tool is chosen

        :returns: None
        """
        self.change_toolbar_state(self.ID_TOOL_FLOOD_ADD)
        self.controller.change_mode(self.ID_TOOL_FLOOD_ADD)

    def on_flood_remove_tool(self):
        """
        Called when the flood remove tool is chosen

        :returns: None
        """
        self.change_toolbar_state(self.ID_TOOL_FLOOD_REMOVE)
        self.controller.change_mode(self.ID_TOOL_FLOOD_REMOVE)

    def on_prev_tool(self):
        """
        Called when the previous patch button is chosen

        :returns: None
        """
        self.controller.prev_patch()

    def on_next_tool(self):
        """
        Called when the next patch button is chosen

        :returns: None
        """
        self.controller.next_patch()

    def on_mousewheel(self, event):
        """
        Called when the mouse wheel is scrolled

        :returns: None
        """
        self.logger.debug("Mouse Wheel {} {}".format(event.delta, event.num))

        # Linux events are weird
        if event.num == 4:
            rotation = -120
        elif event.num == 5:
            rotation = 120

        # Capture windows and mac events
        if event.delta != 0:
            rotation = event.delta

        self.controller.handle_mouse_wheel(rotation)
