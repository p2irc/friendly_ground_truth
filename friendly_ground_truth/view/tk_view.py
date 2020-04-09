"""
File Name: tk_view.py

Authors: Kyle Seidenthal

Date: 06-04-2020

Description: Tkinter Version of the GUI

"""
import tkinter as tk
import os

from tkinter import LEFT, TOP, X, FLAT, RAISED, SUNKEN, ALL
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

    MAX_SCALE = 16
    MIN_SCALE = 0.25

    def __init__(self, controller, master):

        super().__init__()
        Frame.__init__(self, master=None)

        self.master = master
        self.controller = controller

        self.image_scale = 1
        self.image_x = 0
        self.image_y = 0
        self.image_id = None

        self.brush_radius = 0
        self.zoom_cursor = False
        self.flood_cursor = False
        self.brush_cursor = None

        self.previous_position = (0, 0)

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

        self.bind_all("<B1-Motion>", self.on_drag)
        self.bind_all("<Button-1>", self.on_click)
        self.bind_all("<KeyPress>", self.on_keypress)
        self.bind_all("<Left>", self.on_left)
        self.bind_all("<Right>", self.on_right)


    def create_canvas(self):
        """
        Set up a canvas for displaying images

        :returns: None
        """

        self.canvas = tk.Canvas(self, cursor='none', width=1000, height=1000)
        self.canvas.bind_all("<Enter>", self.on_enter_canvas)
        self.canvas.bind_all("<Leave>", self.on_leave_canvas)
        self.canvas.bind_all("<Motion>", self.on_motion)

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

    def on_left(self, event):
        """
        Called when the left arrow key is pressed

        :param event: The event
        :returns: None
        """

        self.on_prev_tool()

    def on_right(self, event):
        """
        Called when the right arrow key is pressed

        :param event: Ethe event
        :returns: None
        """

        self.on_next_tool()

    def on_keypress(self, event):
        """
        Called when a key on the keyboard is pressed

        :param event: The event
        :returns: None
        """

        key = event.char

        if key == 'x':
            self.on_no_root_tool()

        elif key == "t":
            self.on_threshold_tool()

        elif key == "z":
            self.on_zoom_tool()

        elif key == "a":
            self.on_add_reg_tool()

        elif key == "r":
            self.on_remove_reg_tool()

        elif key == "f":
            self.on_flood_add_tool()

        elif key == "l":
            self.on_flood_remove_tool()

        else:
            self.logger.debug("Keypress: {}".format(key))

    def on_load_image(self):
        """
        Called when the load image button is chosen

        :returns: None
        """
        self.controller.load_new_image()
        self.old_img = None

    def show_image(self, img):
        """
        Display the given image in the main window

        :param img: The image to display
        :returns: None
        """

        if self.image_id:
            self.canvas.delete(self.image_id)

        self.current_image = img

        image = Image.fromarray(img)

        self.display_img = ImageTk.PhotoImage(image=image,
                                              master=self.master)
        iw, ih = image.size

        size = int(iw * self.image_scale), int(ih * self.image_scale)

        self.display_img = ImageTk.PhotoImage(image=image.resize(size))

        x, y = self.image_x, self.image_y

        self.image_id = self.canvas.create_image(x, y, anchor="nw",
                                                 image=self.display_img)
        self.canvas.scale(ALL, x, y, self.image_scale, self.image_scale)

        self.canvas.pack()
        self.logger.debug("Image displayed")

    def on_save_mask(self):
        """
        Called when the save mask button is chosem

        :returns: None
        """
        self.controller.save_mask()

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
            rotation = 120
        elif event.num == 5:
            rotation = -120

        # Capture windows and mac events
        if event.delta != 0:
            rotation = event.delta

        self.controller.handle_mouse_wheel(rotation)

    def on_drag(self, event):
        """
        called when the mouse is dragged while the left button is clicked

        :param event: the mouse event
        :returns: none
        """

        self.controller.handle_motion((event.x, event.y))
        self.previous_position = (event.x, event.y)

    def on_motion(self, event):
        """
        Called when the mouse is moved on the canvas

        :param event: The event
        :returns: None
        """

        pos = event.x, event.y

        if not self.zoom_cursor and not self.flood_cursor:
            self.draw_brush(pos)

    def draw_brush(self, pos=None):
        """
        Draw the paintbrush curost

        :param pos: The position to draw at
        :returns: None
        """

        if self.brush_cursor is not None:
            self.canvas.delete(self.brush_cursor)

        if pos is None:
            pos = self.previous_position

        x_max = pos[0] + self.brush_radius
        x_min = pos[0] - self.brush_radius
        y_max = pos[1] + self.brush_radius
        y_min = pos[1] - self.brush_radius

        self.brush_cursor = self.canvas.create_oval(x_max, y_max, x_min, y_min,
                                                    outline='black')

    def on_click(self, event):
        """
        Called when the left mouse button is clicked

        :param event: The mouse event
        :returns: None
        """
        self.previous_position = (event.x, event.y)
        self.controller.handle_left_click((event.x, event.y))

    def set_brush_radius(self, radius):
        """
        Set the radius of the brush cursor representing the current brush

        :param radius: The radius to draw the brush
        :returns: None
        """

        self.brush_radius = radius

    def on_enter_canvas(self, event):
        """
        Called when the cursor enters the canvas

        :param event: The event
        :returns: None
        """

        if self.zoom_cursor:
            self.canvas.config(cursor='sizing')

        elif self.flood_cursor:
            self.canvas.config(cursor='cross')

        else:
            self.canvas.config(cursor='none')

    def on_leave_canvas(self, event):
        """
        Called when the mouse cursor leaves the canvas

        :param event: The event
        :returns: none
        """

        # Toto, I don't think we're in canvas anymore...
        pass



