"""
File Name: view.py

Authors: Kyle Seidenthal

Date: 20-02-2020

Description: Classes that represent the view for the application

"""

import wx
import logging
import numpy as np


module_logger = logging.getLogger('friendly_gt.view')


class MainWindow(wx.Frame):
    """
    The main window for displaying image patches and such
    """

    def __init__(self, controller, parent=None):
        """
        Initializes the main window

        :param controller: The controller to communicate with
        :param parent: The parent frame for this frame
                       The default value is None.
        :returns: None
        """
        self.controller = controller

        # Initialize the logger
        self.logger = logging.getLogger('friendly_gt.view.MainWindow')

        # Constant button IDs
        self.ID_TOOL_THRESH = 101
        self.ID_TOOL_ADD = 102
        self.ID_TOOL_REMOVE = 103

        # Create the frame
        wx.Frame.__init__(self, parent, -1, "Main Window")
        self.logger.debug("Window created successfully")

        self.panel = wx.Panel(self)

        # Set up the interface
        self.init_ui()

        wx.GetApp().Bind(wx.EVT_MOUSEWHEEL, self.on_mousewheel)

    def init_ui(self):
        """
        Initialize the user interface with menus

        :returns: None
        """

        # Create a new menubar
        menubar = wx.MenuBar()

        # ---- File Menu ----
        file_menu = wx.Menu()

        load_item = wx.MenuItem(file_menu, wx.ID_OPEN, text="Load Image",
                                kind=wx.ITEM_NORMAL)
        # TODO: make an icon
        # load_item.SetBitmap(wx.Bitmap("load_item.bmp"))

        file_menu.Append(load_item)

        file_menu.AppendSeparator()

        # ---- End File Menu ----

        menubar.Append(file_menu, '&File')

        # ---- Tool Bar ----

        tool_bar = self.CreateToolBar()

        threshold_tool = tool_bar.AddRadioTool(self.ID_TOOL_THRESH,
                "Threshold",
                wx.Bitmap("view/icons/1x/baseline_tune_black_18dp.png"))

        add_tool = tool_bar.AddRadioTool(self.ID_TOOL_ADD, "Add Region",
                wx.Bitmap("view/icons/1x/baseline_add_circle_outline_black_18dp.png"))

        remove_tool = tool_bar.AddRadioTool(self.ID_TOOL_REMOVE, "Remove\
                Region",
                wx.Bitmap("view/icons/1x/baseline_remove_circle_outline_black_18dp.png"))

        tool_bar.Bind(wx.EVT_TOOL, self.on_tool_chosen)
        tool_bar.Realize()

        # ---- End Tool Bar ----

        # ---- Image Panel ----
        img_data = wx.Image(100, 100)
        self.image_ctrl = wx.StaticBitmap(self.panel, wx.ID_ANY,
                                          wx.Bitmap(img_data))


        prev_button = wx.Button(self.panel, label="Prev")
        prev_button.Bind(wx.EVT_BUTTON, self.on_prev_patch)

        next_button = wx.Button(self.panel, label="Next")
        next_button.Bind(wx.EVT_BUTTON, self.on_next_patch)



        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.main_sizer.Add(wx.StaticLine(self.panel, wx.ID_ANY),
                            0, wx.CENTER)

        self.main_sizer.Add(self.image_ctrl, 0, wx.CENTER, 5)
        self.sizer.Add(prev_button, 0, wx.RIGHT, 5)
        self.sizer.Add(next_button, 0, wx.RIGHT, 5)

        self.main_sizer.Add(self.sizer, 0, wx.ALL, 5)

        self.panel.SetSizer(self.main_sizer)
        self.main_sizer.Fit(self)
        self.panel.Layout()
        # ---- End Image Panel ----

        self.SetMenuBar(menubar)
        self.Bind(wx.EVT_MENU, self.menu_handler)
        self.SetSize((1200, 800))
        self.Centre()

    def show_image(self, img):
        """
        Display the given image in the main window

        :param img: The image to display
        :returns: None
        """
        self.logger.debug("Displaying new image- {}".format(img.shape))

        image = wx.Image(img.shape[1], img.shape[0])
        image.SetData(img.tostring())

        self.image_ctrl.SetBitmap(wx.Bitmap(image))
        self.panel.Refresh()

    def menu_handler(self, event):
        """
        Called when the menu is interacted with

        :param event: The event causing this handler to be called
        :returns: None
        """
        id = event.GetId()

        # If load image was selected
        if id == wx.ID_OPEN:
            self.logger.debug("Load Image Selected")
            self.controller.load_new_image()

    def on_next_patch(self, event):
        """
        Called when the next patch button is pressed

        :param event: The click event
        :returns: None
        """
        self.logger.debug("NEXT IMAGE")

        self.controller.next_patch()

    def on_prev_patch(self, event):
        """
        Called when the previous patch button is pressed

        :param event: The click event
        :returns: None
        """
        self.logger.debug("PREV IMAGE")
        self.controller.prev_patch()

    def on_tool_chosen(self, event):
        """
        Called when a tool is selected from the tool bar

        :param event: The event causing the tool bar click
        :returns: {% A thing %}
        """

        # Threshold tool selected
        if event.GetId() == self.ID_TOOL_THRESH:
            self.logger.debug("Threshold Tool Selected")
            self.controller.change_mode(self.ID_TOOL_THRESH)

        # Add region tool selected
        elif event.GetId() == self.ID_TOOL_ADD:
            self.logger.debug("Add Tool Selected")
            self.controller.change_mode(self.ID_TOOL_ADD)
        # Remove region tool selected
        elif event.GetId() == self.ID_TOOL_REMOVE:
            self.logger.debug("Remove Tool Selected")
            self.controller.change_mode(self.ID_TOOL_REMOVE)

        # Something went wrong
        else:
            self.logger.error("Uh oh, something went wrong selecting a tool")

    def on_mousewheel(self, event):
        """
        Called when the mousewheel is used

        :param event: The mouse wheel event
        :returns: None
        """

        self.logger.debug("mouse wheel scroll! {}"
                .format(event.GetWheelRotation()))

        self.controller.handle_mouse_wheel(event.GetWheelRotation())

