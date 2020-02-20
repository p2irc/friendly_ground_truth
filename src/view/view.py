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

        # Create the frame
        wx.Frame.__init__(self, parent, -1, "Main Window")
        self.logger.debug("Window created successfully")


        self.panel = wx.Panel(self)

        # Set up the interface
        self.init_ui()

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

        # ---- Image Panel ----
        img_data = wx.EmptyImage(1000, 1000)
        self.image_ctrl = wx.StaticBitmap(self.panel, wx.ID_ANY,
                wx.Bitmap(img_data))


        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.mainSizer.Add(wx.StaticLine(self.panel, wx.ID_ANY),
                           0, wx.ALL|wx.EXPAND, 5)

        self.mainSizer.Add(self.image_ctrl, 0, wx.ALL, 5)
        self.mainSizer.Add(self.sizer, 0, wx.ALL, 5)

        self.panel.SetSizer(self.mainSizer)
        self.mainSizer.Fit(self)
        self.panel.Layout()
        # ---- End Image Panel ----

        self.SetMenuBar(menubar)
        self.Bind(wx.EVT_MENU, self.menu_handler)
        self.SetSize((350, 250))
        self.Centre()

    def show_image(self, img):
        """
        Display the given image in the main window

        :param img: The image to display
        :returns: None
        """
        self.logger.debug("Displaying new image")

        image = wx.EmptyImage(img.shape[1], img.shape[0])
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




