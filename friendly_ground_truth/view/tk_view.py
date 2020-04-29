"""
File Name: tk_view.py

Authors: Kyle Seidenthal

Date: 06-04-2020

Description: Tkinter Version of the GUI

"""
import tkinter as tk
import tkinter.messagebox

from io import BytesIO
import base64

from tkinter import LEFT, TOP, X, FLAT, RAISED, SUNKEN, ALL, BOTH, YES
from tkinter import Frame
from tkinter import ttk


from PIL import Image
from PIL import ImageTk as itk
from sys import platform

from friendly_ground_truth.view.icons.icon_strings import (add_region_icon,
                                                           remove_region_icon,
                                                           threshold_icon,
                                                           next_patch_icon,
                                                           prev_patch_icon,
                                                           flood_add_icon,
                                                           flood_remove_icon,
                                                           no_root_icon,
                                                           # add_tip_icon,
                                                           # add_branch_icon,
                                                           # add_cross_icon,
                                                           # remove_land_icon
                                                           )

from friendly_ground_truth.version_info import VersionInfo

import webbrowser

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
    ID_TOOL_ADD_TIP = 110
    ID_TOOL_ADD_CROSS = 111
    ID_TOOL_ADD_BRANCH = 112
    ID_TOOL_REMOVE_LANDMARK = 113
    ID_ADJUST_TOOL = 114

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

        self.can_draw = True

        self.previous_position = (0, 0)

        self.ctrl_pressed = False

        # master.geometry("500x300+300+300")
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
        self.bind_all("<ButtonRelease-1>", self.on_click_release)

        self.bind_all("<B2-Motion>", self.on_wheel_motion)
        self.bind_all("<Button-2>", self.on_wheel_click)
        self.bind_all("<ButtonRelease-2>", self.on_wheel_release)

        self.bind_all("<Button-3>", self.on_right_click)

        self.bind_all("<KeyPress>", self.on_keypress)
        self.bind_all("<Left>", self.on_left)
        self.bind_all("<Right>", self.on_right)

    def create_canvas(self):
        """
        Set up a canvas for displaying images

        :returns: None
        """

        self.canvas = ResizingCanvas(self, cursor='none')
        self.canvas.bind("<Enter>", self.on_enter_canvas)
        self.canvas.bind("<Leave>", self.on_leave_canvas)
        self.canvas.bind("<Motion>", self.on_motion)
        self.canvas.pack(fill=BOTH, expand=YES)

    def create_menubar(self):
        """
        Create the menu bar

        :returns: None
        """

        self.menubar = tk.Menu(self.master)

        self.create_file_menu()

        self.create_help_menu()

        self.create_toolbar()

        self.master.config(menu=self.menubar)

    def create_help_menu(self):
        """
        Create the help menu bar

        :returns: None
        """

        self.helpmenu = tk.Menu(self.menubar, tearoff=0)

        self.helpmenu.add_command(label="About",
                                  command=self.on_about)

        self.helpmenu.add_command(label="Keyboard Shortcuts",
                                  command=self.on_keyboard_shortcuts)

        self.menubar.add_cascade(label="Help", menu=self.helpmenu)

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
        thresh_data = Image.open(BytesIO(base64.b64decode(threshold_icon)))
        thresh_img = itk.PhotoImage(thresh_data)
        thresh_button = tk.Button(self.toolbar, image=thresh_img,
                                  relief=FLAT, command=self.on_threshold_tool)
        thresh_button.image = thresh_img
        thresh_button.pack(side=LEFT, padx=2, pady=2)

        # Add Region Button
        add_region_data = Image.open(BytesIO(base64.
                                             b64decode(add_region_icon)))
        add_reg_img = itk.PhotoImage(add_region_data)

        add_reg_button = tk.Button(self.toolbar, image=add_reg_img,
                                   relief=FLAT, command=self.on_add_reg_tool)
        add_reg_button.image = add_reg_img
        add_reg_button.pack(side=LEFT, padx=2, pady=2)

        # Remove Region Button
        remove_region_data = Image.open(BytesIO(base64.
                                                b64decode(remove_region_icon)))
        remove_reg_img = itk.PhotoImage(remove_region_data)
        remove_reg_button = tk.Button(self.toolbar, image=remove_reg_img,
                                      relief=FLAT,
                                      command=self.on_remove_reg_tool)
        remove_reg_button.image = remove_reg_img
        remove_reg_button.pack(side=LEFT, padx=2, pady=2)

        # Flood Add Button
        flood_add_data = Image.open(BytesIO(base64.b64decode(flood_add_icon)))
        flood_add_img = itk.PhotoImage(flood_add_data)
        flood_add_button = tk.Button(self.toolbar, image=flood_add_img,
                                     relief=FLAT,
                                     command=self.on_flood_add_tool)
        flood_add_button.image = flood_add_img
        flood_add_button.pack(side=LEFT, padx=2, pady=2)

        # Flood Remove Button
        flood_remove_data = Image.open(BytesIO(base64.
                                               b64decode(flood_remove_icon)))
        flood_remove_img = itk.PhotoImage(flood_remove_data)
        flood_remove_button = tk.Button(self.toolbar, image=flood_remove_img,
                                        relief=FLAT,
                                        command=self.on_flood_remove_tool)
        flood_remove_button.image = flood_remove_img
        flood_remove_button.pack(side=LEFT, padx=2, pady=2)

        # No Root Button
        no_root_data = Image.open(BytesIO(base64.b64decode(no_root_icon)))
        no_root_img = itk.PhotoImage(no_root_data)
        no_root_button = tk.Button(self.toolbar, image=no_root_img,
                                   relief=FLAT,
                                   command=self.on_no_root_tool)
        no_root_button.image = no_root_img
        no_root_button.pack(side=LEFT, padx=2, pady=2)

        # Prev Button
        prev_data = Image.open(BytesIO(base64.b64decode(prev_patch_icon)))
        prev_img = itk.PhotoImage(prev_data)
        prev_button = tk.Button(self.toolbar, image=prev_img,
                                relief=FLAT,
                                command=self.on_prev_tool)
        prev_button.image = prev_img
        prev_button.pack(side=LEFT, padx=2, pady=2)

        # Next Button
        next_data = Image.open(BytesIO(base64.b64decode(next_patch_icon)))
        next_img = itk.PhotoImage(next_data)
        next_button = tk.Button(self.toolbar, image=next_img,
                                relief=FLAT,
                                command=self.on_next_tool)
        next_button.image = next_img
        next_button.pack(side=LEFT, padx=2, pady=2)

        # Add Tip Button
        # add_tip_data = Image.open(BytesIO(base64.b64decode(add_tip_icon)))
        # add_tip_img = itk.PhotoImage(add_tip_data)

        # add_tip_button = tk.Button(self.toolbar, image=add_tip_img,
        #                           relief=FLAT, command=self.on_add_tip_tool)
        # add_tip_button.image = add_tip_img
        # add_tip_button.pack(side=LEFT, padx=2, pady=2)

        # Add Cross Button
        # add_cross_data = Image.\
        #        open(BytesIO(base64.b64decode(add_cross_icon)))
        # add_cross_img = itk.PhotoImage(add_cross_data)

        # add_cross_button = tk.Button(self.toolbar, image=add_cross_img,
        #                              relief=FLAT,
        #                              command=self.on_add_cross_tool)
        # add_cross_button.image = add_cross_img
        # add_cross_button.pack(side=LEFT, padx=2, pady=2)

        # Add Branch Button
        # add_branch_data = Image.open(BytesIO(base64
        #                                      .b64decode(add_branch_icon)))
        # add_branch_img = itk.PhotoImage(add_branch_data)
        # add_branch_button = tk.Button(self.toolbar, image=add_branch_img,
        #                               relief=FLAT,
        #                               command=self.on_add_branch_tool)
        # add_branch_button.image = add_branch_img
        # add_branch_button.pack(side=LEFT, padx=2, pady=2)

        # Remove Landmark Button
        # remove_landmark_data = Image.open(BytesIO(base64.
        #                                           b64decode(remove_land_icon)))
        # remove_landmark_img = itk.PhotoImage(remove_landmark_data)

        # remove_landmark_button = tk.Button(self.toolbar,
        #                                    image=remove_landmark_img,
        #                                    relief=FLAT,
        #                                    command=self.
        #                                    on_remove_landmark_tool)

        # remove_landmark_button.image = remove_landmark_img
        # remove_landmark_button.pack(side=LEFT, padx=2, pady=2)

        self.orig_button_colour = remove_reg_button.cget("background")

        self.toolbar_buttons[self.ID_TOOL_THRESH] = thresh_button
        self.toolbar_buttons[self.ID_TOOL_ADD] = add_reg_button
        self.toolbar_buttons[self.ID_TOOL_REMOVE] = remove_reg_button
        self.toolbar_buttons[self.ID_TOOL_NO_ROOT] = no_root_button
        self.toolbar_buttons[self.ID_TOOL_PREV_IMAGE] = prev_button
        self.toolbar_buttons[self.ID_TOOL_NEXT_IMAGE] = next_button
        self.toolbar_buttons[self.ID_TOOL_FLOOD_ADD] = flood_add_button
        self.toolbar_buttons[self.ID_TOOL_FLOOD_REMOVE] = flood_remove_button
        # self.toolbar_buttons[self.ID_TOOL_ADD_TIP] = add_tip_button
        # self.toolbar_buttons[self.ID_TOOL_ADD_CROSS] = add_cross_button
        # self.toolbar_buttons[self.ID_TOOL_ADD_BRANCH] = add_branch_button
        # self.toolbar_buttons[self.ID_TOOL_REMOVE_LANDMARK] = \
        #    remove_landmark_button

        self.toolbar.pack(side=TOP, fill=X)

        self.pack()

    def on_about(self):
        """
        Display the about dialog

        :param event: The event
        :returns: None
        """
        AboutDialog()

    def on_keyboard_shortcuts(self):
        """
        Display the keyboard shortcut dialog

        :returns: None
        """
        KeyboardShortcutDialog()

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

        s = event.state
        ctrl = (s & 0x4) != 0
        alt = (s & 0x8) != 0 or (s & 0x80) != 0
        shift = (s & 0x1) != 0

        if shift:
            key = 'shift+' + key

        if alt:
            key = 'alt+' + key

        if ctrl:
            key = 'ctrl+' + key

        if key == 'x':
            self.on_no_root_tool()

        elif key == "t":
            self.on_threshold_tool()

        elif key == "a":
            self.on_add_reg_tool()

        elif key == "r":
            self.on_remove_reg_tool()

        elif key == "f":
            self.on_flood_add_tool()

        elif key == "l":
            self.on_flood_remove_tool()

        # elif key == "c":
        #    self.on_add_cross_tool()

        # elif key == "v":
        #    self.on_add_tip_tool()

        # elif key == "b":
        #     self.on_add_branch_tool()

        # elif key == "n":
        #    self.on_remove_landmark_tool()
        else:
            self.logger.debug("Keypress: {}".format(key))

    def on_load_image(self):
        """
        Called when the load image button is chosen

        :returns: None
        """

        self.controller.load_new_image()
        self.old_img = None

    def start_progressbar(self, num_patches):
        """
        Start displaying a progressbar

        :returns: None
        """
        self.prog_popup = tk.Toplevel()

        self.prog_popup.geometry("100x50+500+400")

        tk.Label(self.prog_popup, text="Image Loading").grid(row=0, column=0)

        self.load_progress = 0
        self.load_prog_var = tk.DoubleVar()
        self.load_prog_bar = ttk.Progressbar(self.prog_popup,
                                             variable=self.load_prog_var,
                                             maximum=100)
        self.load_prog_bar.grid(row=1, column=0)

        self.progress_step = float(100.0/num_patches)
        self.prog_popup.pack_slaves()

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

        self.display_img = itk.PhotoImage(image=image,
                                          master=self.master)
        iw, ih = image.size

        size = int(iw * self.image_scale), int(ih * self.image_scale)

        self.display_img = itk.PhotoImage(image=image.resize(size))

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
                if platform != "darwin":
                    button.config(relief=SUNKEN)
                button.config(bg="yellow")

            else:
                if platform != "darwin":
                    button.config(relief=RAISED)

                button.config(bg=self.orig_button_colour)

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

    # def on_add_tip_tool(self):
    #     """
    #     Called when the add tip brush tool is chosen

    #     :returns: None
    #     """

    #     self.change_toolbar_state(self.ID_TOOL_ADD_TIP)

    #     self.controller.change_mode(self.ID_TOOL_ADD_TIP)

    # def on_add_cross_tool(self):
    #     """
    #     Called when the add cross brush tool is chosen

    #     :returns: None
    #     """

    #     self.change_toolbar_state(self.ID_TOOL_ADD_CROSS)

    #     self.controller.change_mode(self.ID_TOOL_ADD_CROSS)

    # def on_add_branch_tool(self):
    #     """
    #     Called when the add branch brush tool is chosen

    #     :returns: None
    #     """

    #     self.change_toolbar_state(self.ID_TOOL_ADD_BRANCH)

    #     self.controller.change_mode(self.ID_TOOL_ADD_BRANCH)

    # def on_remove_landmark_tool(self):
    #     """
    #     Called when the remoive landmark brush tool is chosen

    #     :returns: None
    #     """

    #     self.change_toolbar_state(self.ID_TOOL_REMOVE_LANDMARK)

    #     self.controller.change_mode(self.ID_TOOL_REMOVE_LANDMARK)

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

        self.previous_position = event.x, event.y
        s = event.state

        alt = (s & 0x8) != 0 or (s & 0x80) != 0

        if alt:
            self.controller.change_secondary_mode(self.ID_ADJUST_TOOL)

        self.controller.handle_mouse_wheel(rotation, event.x, event.y)
        self.controller.change_secondary_mode(self.ID_TOOL_ZOOM)

    def on_drag(self, event):
        """
        called when the mouse is dragged while the left button is clicked

        :param event: the mouse event
        :returns: none
        """
        state = event.state
        ctrl = (state & 0x4) != 0

        if not ctrl:
            self.controller.handle_motion((event.x, event.y))
        else:
            self.canvas.config(cursor="hand2")
            self.controller.handle_mouse_wheel_motion((event.x, event.y))

        self.previous_position = (event.x, event.y)
        self.on_motion(event)

    def on_wheel_motion(self, event):
        """
        Called when the mouuse is dragged with the mouswheel pressed

        :param event: The mouse event
        :returns: None
        """

        self.controller.handle_mouse_wheel_motion((event.x, event.y))
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
                                                    outline='white')

    def on_wheel_click(self, event):
        """
        Called when the mouse wheel is clicekd

        :param event: The Mouse event
        :returns: None
        """
        self.canvas.config(cursor="hand2")
        self.previous_position = (event.x, event.y)

    def on_wheel_release(self, event):
        """
        Called when the mouse wheel is released

        :param event: THe mouse event
        :returns: None
        """
        self.on_enter_canvas(event)

    def on_click(self, event):
        """
        Called when the left mouse button is clicked

        :param event: The mouse event
        :returns: None
        """
        self.previous_position = (event.x, event.y)

        self.logger.debug("Click location: {}, {}".format(event.x, event.y))

        if self.can_draw:
            self.controller.handle_left_click((event.x, event.y))

    def on_click_release(self, event):
        """
        Called when the left mouse button is released

        :param event: Mouse Event
        :returns: None
        """
        self.on_enter_canvas(None)

    def on_right_click(self, event):
        """
        Called when the right mouse button is clicked

        :param event: The mouse event
        :returns: None
        """
        self.logger.debug("Right Click")
        if self.can_draw:
            self.controller.handle_right_click()

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
        self.can_draw = True
        if self.flood_cursor:
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
        self.can_draw = False


class AboutDialog(tk.Toplevel):

    def __init__(self):
        self.base = tk.Toplevel()
        self.base.title("About")

        version_info = VersionInfo()
        current_version = version_info.get_version_string()

        latest = version_info.check_for_update()

        version_text = ("You are currently using version " +
                        current_version + " ")

        version_text += latest

        self.version_link = ("https://github.com/KyleS22/friendly_ground" +
                             "_truth/releases/latest")

        manual_text = " A user manual can be found at: "
        self.manual_link = ("https://github.com/KyleS22/friendly_ground" +
                            "_truth/wiki/User-Manual")

        bug_text = "Found a bug?  Please report it at:"
        self.bug_link = ("https://github.com/KyleS22/friendly_ground_truth" +
                         "/issues")

        self.version_label = tk.Label(self.base, text=version_text)
        self.version_label.pack(pady=15)

        if version_info.check_newer_version(version_info.
                                            get_newest_release_info()):
            self.version_link_label = tk.Label(self.base,
                                               text=self.version_link,
                                               fg="blue", cursor="hand2")
            self.version_link_label.pack(pady=15)
            self.version_link_label.bind("<Button-1>", self.on_version_click)

        self.manual_label = tk.Label(self.base, text=manual_text)
        self.manual_label.pack(pady=15)

        self.manual_link_label = tk.Label(self.base, text=self.manual_link,
                                          fg="blue", cursor="hand2")
        self.manual_link_label.pack(pady=15)
        self.manual_link_label.bind("<Button-1>", self.on_manual_click)

        self.bug_label = tk.Label(self.base, text=bug_text)
        self.bug_label.pack(pady=15)

        self.bug_link_label = tk.Label(self.base, text=self.bug_link,
                                       fg="blue", cursor="hand2")
        self.bug_link_label.pack(pady=15)
        self.bug_link_label.bind("<Button-1>", self.on_bug_click)

    def on_version_click(self, event):
        webbrowser.open(self.version_link)

    def on_manual_click(self, event):
        webbrowser.open(self.manual_link)

    def on_bug_click(self, event):
        webbrowser.open(self.bug_link)


class KeyboardShortcutDialog(tk.Toplevel):

    def __init__(self):
        self.base = tk.Toplevel()
        self.base.title("Keyboard Shortcuts")

        thresh_data = Image.open(BytesIO(base64.b64decode(threshold_icon)))
        thresh_img = itk.PhotoImage(thresh_data)

        thresh_img_label = tk.Label(self.base, image=thresh_img)
        thresh_img_label.image = thresh_img
        thresh_img_label.grid(row=0, column=0)

        thresh_label = tk.Label(self.base, text="Threshold Tool (t)")
        thresh_label.grid(row=0, column=1)

        space_label = tk.Label(self.base, text="    ")
        space_label.grid(row=0, column=2)

        add_reg_data = Image.open(BytesIO(base64.b64decode(add_region_icon)))
        add_reg_img = itk.PhotoImage(add_reg_data)

        add_reg_img_label = tk.Label(self.base, image=add_reg_img)
        add_reg_img_label.image = add_reg_img
        add_reg_img_label.grid(row=0, column=3)

        add_reg_label = tk.Label(self.base, text="Add Region Tool (a)")
        add_reg_label.grid(row=0, column=4)

        space_label = tk.Label(self.base, text="    ")
        space_label.grid(row=0, column=5)

        rem_reg_data = Image.open(BytesIO(base64.
                                  b64decode(remove_region_icon)))
        rem_reg_img = itk.PhotoImage(rem_reg_data)

        rem_reg_img_label = tk.Label(self.base, image=rem_reg_img)
        rem_reg_img_label.image = rem_reg_img
        rem_reg_img_label.grid(row=0, column=6)

        rem_reg_label = tk.Label(self.base, text="Remove Region Tool (r)")
        rem_reg_label.grid(row=0, column=7)

        # space_label = tk.Label(self.base, text="    ")
        # space_label.grid(row=1, column=2)

        flood_add_data = Image.open(BytesIO(base64.b64decode(flood_add_icon)))
        flood_add_reg_img = itk.PhotoImage(flood_add_data)

        flood_add_reg_img_label = tk.Label(self.base, image=flood_add_reg_img)
        flood_add_reg_img_label.image = flood_add_reg_img
        flood_add_reg_img_label.grid(row=1, column=0)

        flood_add_reg_label = tk.Label(self.base, text="Flood Add Tool (f)")
        flood_add_reg_label.grid(row=1, column=1)

        space_label = tk.Label(self.base, text="    ")
        space_label.grid(row=1, column=2)

        flood_remove_data = Image.open(BytesIO(base64.
                                       b64decode(flood_remove_icon)))
        flood_rem_reg_img = itk.PhotoImage(flood_remove_data)

        flood_rem_reg_img_label = tk.Label(self.base, image=flood_rem_reg_img)
        flood_rem_reg_img_label.image = flood_rem_reg_img
        flood_rem_reg_img_label.grid(row=1, column=3)

        flood_rem_reg_label = tk.Label(self.base, text="Flood Remove Tool (l)")
        flood_rem_reg_label.grid(row=1, column=4)

        no_root_data = Image.open(BytesIO(base64.b64decode(no_root_icon)))
        no_root_img = itk.PhotoImage(no_root_data)

        no_root_img_label = tk.Label(self.base, image=no_root_img)
        no_root_img_label.image = no_root_img
        no_root_img_label.grid(row=2, column=6)

        no_root_label = tk.Label(self.base, text="No Root Tool (x)")
        no_root_label.grid(row=2, column=7)

        space_label = tk.Label(self.base, text="    ")
        space_label.grid(row=2, column=5)

        prev_img_data = Image.open(BytesIO(base64.b64decode(prev_patch_icon)))
        prev_img = itk.PhotoImage(prev_img_data)

        prev_img_label = tk.Label(self.base, image=prev_img)
        prev_img_label.image = prev_img
        prev_img_label.grid(row=2, column=0)

        prev_label = tk.Label(self.base, text="Previous Patch (Left-Arrow)")
        prev_label.grid(row=2, column=1)

        space_label = tk.Label(self.base, text="    ")
        space_label.grid(row=2, column=2)

        next_patch_data = Image.open(BytesIO(base64.
                                     b64decode(next_patch_icon)))
        next_img = itk.PhotoImage(next_patch_data)

        next_img_label = tk.Label(self.base, image=next_img)
        next_img_label.image = next_img
        next_img_label.grid(row=2, column=3)

        next_label = tk.Label(self.base, text="Next Patch (Right-Arrow)")
        next_label.grid(row=2, column=4)

        #  add_tip_data = Image.open(BytesIO(base64.b64decode(add_tip_icon)))
        #  add_tip_img = itk.PhotoImage(add_tip_data)

        #  add_tip_img_label = tk.Label(self.base, image=add_tip_img)
        #  add_tip_img_label.image = add_tip_img
        #  add_tip_img_label.grid(row=3, column=6)

        #  add_tip_label = tk.Label(self.base, text="Add Root Tip (v)")
        #  add_tip_label.grid(row=3, column=7)

        # space_label = tk.Label(self.base, text="    ")
        # space_label.grid(row=3, column=5)

        # add_cross_data = Image.\
        #        open(BytesIO(base64.b64decode(add_cross_icon)))
        # add_cross_img = itk.PhotoImage(add_cross_data)

        # add_cross_img_label = tk.Label(self.base, image=add_cross_img)
        # add_cross_img_label.image = add_cross_img
        # add_cross_img_label.grid(row=3, column=0)

        # add_cross_label = tk.Label(self.base, text="Add Root Crossing (c)")
        # add_cross_label.grid(row=3, column=1)

        # space_label = tk.Label(self.base, text="    ")
        # space_label.grid(row=3, column=2)

        # add_branch_data = Image.open(BytesIO(base64.
        #                              b64decode(add_branch_icon)))
        # add_branch_img = itk.PhotoImage(add_branch_data)

        # add_branch_img_label = tk.Label(self.base, image=add_branch_img)
        # add_branch_img_label.image = add_branch_img
        # add_branch_img_label.grid(row=3, column=3)

        # add_branch_label = tk.Label(self.base, text="Add Root Branching (b)")
        # add_branch_label.grid(row=3, column=4)

        # remove_land_data = Image.open(BytesIO(base64
        #                                       .b64decode(remove_land_icon)))
        # remove_landmark_img = itk.PhotoImage(remove_land_data)

        # remove_landmark_img_label = tk.Label(self.base,
        #                                      image=remove_landmark_img)
        # remove_landmark_img_label.image = remove_landmark_img
        # remove_landmark_img_label.grid(row=4, column=0)

        # remove_landmark_label = tk.Label(self.base, \
        #        text="Remove Landmark (n)")
        # remove_landmark_label.grid(row=4, column=1)


class ResizingCanvas(tk.Canvas):

    def __init__(self, parent, **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)

        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    def on_resize(self, event):

        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height

        self.width = event.width
        self.height = event.height

        self.config(width=self.width, height=self.height)
        self.scale("all", 0, 0, wscale, hscale)
