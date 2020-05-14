"""
File Name: main_window.py

Authors: Kyle Seidenthal

Date: 13-05-2020

Description: The main window for the application.

"""

import tkinter as tk
import base64

from tkinter import ttk
from io import BytesIO

from PIL import Image
from PIL import ImageTk as itk

from friendly_ground_truth.view.fgt_canvas import FGTCanvas
from sys import platform

import logging
module_logger = logging.getLogger('friendly_gt.view')


class MainWindow(ttk.Frame):
    """
    The main window for the application.

    Attributes:
        {% An Attribute %}: {% Description %}
    """

    def __init__(self, master, controller):
        """
        Initialize the main window.

        Args:
            master: The root tkinter process.
            controller: The controller logic

        Returns:
            A main window object.
        """

        ttk.Frame.__init__(self, master=master)

        self._master = master
        self._controller = controller

        self._logger = logging.getLogger('friendly_gt.view.MainWindow')

        self._master.title("Friendly Ground Truth")
        self._master.geometry('800x600')
        self._master.rowconfigure(0, weight=1)
        self._master.columnconfigure(0, weight=1)

        self._canvas = None

        self._register_key_mappings()

        self._create_menubar()

        # Interactions
        self._previous_state = 0
        self.bind('<Key>', self._keystroke)

    def create_canvas(self, image):
        """
        Create the image canvas.

        Args:
            image: The image, a numpy array.

        Returns:
            None

        Postconditions:
            self._canvas is set
        """
        if self._canvas is not None:
            self._canvas.destroy()

        self._canvas = FGTCanvas(self.master, image)
        self._canvas.grid(row=1, column=0, sticky="NSEW")
        self._master.grid_rowconfigure(0, weight=0)
        self._master.grid_rowconfigure(1, weight=1)

    def update_canvas_image(self, image):
        """
        Set the current image in the canvas.

        Args:
            image: The image, a numpy array

        Returns:
            None

        Postconditions:
            The canvas's image will be set to the given image data.
        """
        if self._canvas is not None:
            self._canvas.img = image

    def _register_key_mappings(self):
        """
        Register a mapping of tool ids to keys.


        Returns:
            None

        Postconditions:
            self._key_mappings will contain a dictionary of id -> key mappings
        """
        self._key_mappings = {}

        for tool_id in self._controller.image_tools.keys():
            tool = self._controller.image_tools[tool_id]
            self._key_mappings[tool_id] = tool.key_mapping

        self._reverse_key_mappings = {}

        for tool_id in self._key_mappings.keys():
            key = self._key_mappings[tool_id]

            self._reverse_key_mappings[key] = tool_id

    def _keystroke(self, event):
        """
        Called when the keybord is used.

        Args:
            event: The keyboard event.

        Returns:
            None

        Postconditions:
            The canvas is modified according to the key pressed.
        """
        key = ''
        # means that the Control key is pressed
        if event.state - self._previous_state == 4:
            key = "CTRL+"
        else:
            # remember the last keystroke state
            self._previous_state = event.state

        key += event.keysym

        print("KEY: " + key)

        try:
            tool_id = self._reverse_key_mappings[key]
            self._on_tool_selected(tool_id)
        except KeyError:
            print("{} is not a valid key code".format(key))

    def _create_menubar(self):
        """
        Create the menu bar.


        Returns:
            None

        Postconditions:
            The menu bar will be created at the top of the screen.
        """

        self._menubar = tk.Menu(self.master)

        self._create_file_menu()

        self._create_help_menu()

        self._create_toolbar()

        self._master.config(menu=self._menubar)

    def _create_file_menu(self):
        """
        Create the file menu.


        Returns:
            None

        Postconditions:
            The file menu will be popultated.
        """

        self._filemenu = tk.Menu(self._menubar, tearoff=0)

        self._filemenu.add_command(label="Load Image",
                                   command=self._on_load_image)

        self._filemenu.add_command(label="Save Mask",
                                   command=self._on_save_mask)

        self._menubar.add_cascade(label="File", menu=self._filemenu)

    def _create_help_menu(self):
        """
        Create the help menu.


        Returns:
            None

        Postconditions:
            The help menu will be populated.
        """
        self._helpmenu = tk.Menu(self._menubar, tearoff=0)

        self._helpmenu.add_command(label="About",
                                   command=self._on_about)

        self._helpmenu.add_command(label="Keyboard Shortcuts",
                                   command=self._on_keyboard_shortcuts)

        self._menubar.add_cascade(label="Help", menu=self._helpmenu)

    def _create_toolbar(self):
        """
        Create the toolbar.


        Returns:
            None

        Postconditions:
            The toolbar is created.
        """

        self._toolbar = tk.Frame(self._master, bd=1, relief='raised')
        self._toolbar_buttons = {}

        # Create image interaction tools
        image_tools = self._controller.image_tools

        column = 0
        for tool_id in image_tools.keys():
            tool = image_tools[tool_id]

            icon = self._load_icon_from_string(tool.icon_string)
            button = tk.Button(self._toolbar, image=icon, relief='flat',
                               command=lambda: self._on_tool_selected(tool.id))

            button.image = icon
            button.pack(side="left", padx=2, pady=2)
            # button.grid(column=column, row=0, sticky='EW')
            column += 1

            self._create_tool_tip(button, tool.id, tool.name)
            self._toolbar_buttons[tool.id] = button
            self._orig_button_colour = button.cget("background")

        self._image_indicator = tk.Label(self._toolbar, text="No Image Loaded")
        self._image_indicator.pack(side='right', padx=2, pady=2)
        # self._image_indicator.grid(column=column, row=0, sticky='W')
        #self._toolbar.pack(side='top', fill='x')
        self._toolbar.grid(column=0, row=0, sticky='NEW')

    def _on_tool_selected(self, id):
        """
        Called when a tool is selected in the menubar

        Args:
            id: The id of the tool.

        Returns:
            None

        Postconditions:
            The controller is updated to reflect the current chosen tool.
        """
        self._controller.activate_tool(id)

    def _update_toolbar_state(self, tool_id):
        """
        Change the state of the buttons in the toolbar based on the button that
        has been chosen.

        Args:
            tool_id: The id of the tool that was chosen

        Returns:
            None

        Postconditions:
            The toolbar button matching the given id will be activated.
        """
        for id, button in self._toolbar_buttons.items():
            if id == tool_id:
                if platform != "darwin":
                    button.config(relief="sunken")
                button.config(bg="yellow")
            else:
                if platform != "darwin":
                    button.config(relief="raised")
                button.config(bg=self._orig_button_colour)

    def _create_tool_tip(self, button, id, name):
        """
        Create a tool tip for the given button.

        Args:
            button: The button to create the tooltip for.
            id: The id of the tool.
            name: The name of the tool
        Returns:
            None

        Postcondition:
            The tooltip is attached to the button.
        """
        key = self._key_mappings[id]

        tip = name + "(" + key + ")"

        CreateToolTip(button, tip)

    def _load_icon_from_string(self, icon_string):
        """
        Load a tkinter compatible image from an icon bytestring.

        Args:
            icon_string: The 64 bit encoded icon string

        Returns:
            A ImageTK PhotoImage
        """
        data = Image.open(BytesIO(base64.b64decode(icon_string)))
        img = itk.PhotoImage(data)

        return img

    def _on_load_image(self):
        """
        Called when the load image button is chosen


        Returns:
            None

        Postconditions:
            The controllers Image property is set
        """
        self._controller.load_new_image()
        self._old_img = None

    def _on_save_mask(self):
        """
        Called when the save mask button is chosen

        Returns:
            None

        Postcondition:
            The controller will be called to save the mask.

        Returns:
            None
        """
        self._controller.save_mask()

    def _on_about(self):
        """
        Called when the about button is chosen.


        Returns:
            None
        """
        # TODO: start the about window
        pass

    def _on_keyboard_shortcuts(self):
        """
        Called when the keyboard shortcuts button is chosen/


        Returns:
            None
        """
        # TODO: Open keyboard shortcuts window
        pass

    def start_progressbar(self, num_patches):
        """
        Start displaying a progressbar.

        Args:
            num_patches: The number of patches that are being loaded.

        Returns:
            None

        Postconditions:
            A progressbar window is opened and initialized
        """
        self.progress_popup = tk.Toplevel()
        self.progress_popup.geometry("100x50+500+400")

        tk.Label(self.progress_popup, text="Image Loading.").grid(row=0, column=0)

        self.load_progress = 0
        self.load_progress_var = tk.DoubleVar()
        self.load_progress_bar = ttk.Progressbar(self.progress_popup,
                                              variable=self.load_progress_var,
                                              maximum=100)

        self.load_progress_bar.grid(row=1, column=0)

        self.progress_step = float(100.0/num_patches)
        self.progress_popup.pack_slaves()

    def show_image(self, img):
        """
        Display the given image on the canvas.

        Args:
            img: The image to display, a numpy array

        Returns:
            None

        Postconditions:
            The canvas's image will be set to the image.
        """

        if self._canvas is None:
            self.create_canvas(img)
            return

class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     # miliseconds
        self.wraplength = 180   # pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                         background="#ffffff", relief='solid', borderwidth=1,
                         wraplength=self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()
