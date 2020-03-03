"""
File Name: view.py

Authors: Kyle Seidenthal

Date: 20-02-2020

Description: Classes that represent the view for the application

"""

import wx
import logging
import numpy as np
from view.icons import (add_region_icon, remove_region_icon, next_patch_icon,
                        no_root_icon, prev_patch_icon, threshold_icon)

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
        self.current_image = None
        self.brush_radius = 0

        # Initialize the logger
        self.logger = logging.getLogger('friendly_gt.view.MainWindow')

        # Constant button IDs
        self.ID_TOOL_THRESH = 101
        self.ID_TOOL_ADD = 102
        self.ID_TOOL_REMOVE = 103
        self.ID_TOOL_NO_ROOT = 104
        self.ID_TOOL_PREV_IMAGE = 105
        self.ID_TOOL_NEXT_IMAGE = 106

        # Create the frame
        wx.Frame.__init__(self, parent, -1, "Main Window")
        self.logger.debug("Window created successfully")

        # Set up the interface
        self.init_ui()

        # Set up mouse interactions
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

        export_mask = wx.MenuItem(file_menu, wx.ID_SAVE, text="Save Mask",
                                  kind=wx.ITEM_NORMAL)

        file_menu.Append(load_item)
        file_menu.Append(export_mask)

        file_menu.AppendSeparator()

        # ---- End File Menu ----

        menubar.Append(file_menu, '&File')

        # ---- Tool Bar ----

        tool_bar = self.CreateToolBar()

        # Create toolbar bitmaps
        threshold_img = wx.Image(threshold_icon.get_threshold_icon.getImage())
        threshold_bitmap = wx.Bitmap(threshold_img.ConvertToBitmap())

        threshold_tool = tool_bar.AddRadioTool(self.ID_TOOL_THRESH,
                                               "Threshold",
                                               threshold_bitmap)

        add_region_img = wx.Image(add_region_icon.get_add_region_icon.getImage())
        add_region_bitmap = wx.Bitmap(add_region_img.ConvertToBitmap())


        add_tool = tool_bar.AddRadioTool(self.ID_TOOL_ADD, "Add Region",
                                         add_region_bitmap)

        remove_region_img = wx.Image(remove_region_icon.get_remove_region_icon.getImage())
        remove_region_bitmap = wx.Bitmap(remove_region_img.ConvertToBitmap())



        remove_tool = tool_bar.AddRadioTool(self.ID_TOOL_REMOVE, "Remove"
                                                                 "Region",
                                            remove_region_bitmap)


        no_roots_img = wx.Image(no_root_icon.get_no_root_icon.getImage())
        no_roots_bitmap = wx.Bitmap(no_roots_img.ConvertToBitmap())



        no_roots_tool = tool_bar.AddTool(self.ID_TOOL_NO_ROOT, "No Roots",
                                         no_roots_bitmap)

        tool_bar.AddSeparator()


        prev_patch_img = wx.Image(prev_patch_icon.get_prev_patch_icon.getImage())
        prev_patch_bitmap = wx.Bitmap(prev_patch_img.ConvertToBitmap())



        prev_image_tool = tool_bar.AddTool(self.ID_TOOL_PREV_IMAGE,
                                           "Prev Image",
                                           prev_patch_bitmap)

        next_patch_img = wx.Image(next_patch_icon.get_next_patch_icon.getImage())
        next_patch_bitmap = wx.Bitmap(next_patch_img.ConvertToBitmap())



        next_image_tool = tool_bar.AddTool(self.ID_TOOL_NEXT_IMAGE,
                                           "Next Image",
                                           next_patch_bitmap)

        tool_bar.Bind(wx.EVT_TOOL, self.on_tool_chosen)
        tool_bar.Realize()

        # ---- End Tool Bar ----

        # ---- Image Panel ----
        self.control_panel = wx.Panel(self)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.image_panel = wx.Panel(self.control_panel)
        hbox.Add(self.image_panel, wx.ID_ANY, wx.EXPAND | wx.ALL, 20)

        # Mouse Events for the image panel
        self.image_panel.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.image_panel.Bind(wx.EVT_LEFT_UP, self.on_left_up)
        self.image_panel.Bind(wx.EVT_MOTION, self.on_motion)
        self.image_panel.Bind(wx.EVT_PAINT, self.on_paint)
        self.image_panel.Bind(wx.EVT_ENTER_WINDOW, self.on_enter_panel)
        self.image_panel.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave_panel)

        self.control_panel.SetSizer(hbox)

        # ---- Overlay ----
        self.overlay = wx.Overlay()
        # ---- End Overlay ----

        # ---- End Image Panel ----

        self.SetMenuBar(menubar)
        self.Bind(wx.EVT_MENU, self.menu_handler)
        self.SetSize((1200, 800))
        self.Centre()

    def show_image(self, img, dc=None):
        """
        Display the given image in the main window

        :param img: The image to display
        :returns: None
        """
        self.current_image = img

        image = wx.Image(img.shape[1], img.shape[0])
        image.SetData(img.tostring())

        self.bitmap = wx.Bitmap(image)

        if dc is None:
            dc = wx.ClientDC(self.image_panel)
            odc = wx.DCOverlay(self.overlay, dc)
            odc.Clear()

        dc.DrawBitmap(self.bitmap, 0, 0)

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
        elif id == wx.ID_SAVE:
            self.logger.debug("Exporting Mask")
            self.controller.save_mask()

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

        # No Root Tool selected
        elif event.GetId() == self.ID_TOOL_NO_ROOT:
            self.logger.debug("No Root Tool Selected")
            self.controller.change_mode(self.ID_TOOL_NO_ROOT)

        # Next image
        elif event.GetId() == self.ID_TOOL_NEXT_IMAGE:
            self.controller.next_patch()

        # Previous Image
        elif event.GetId() == self.ID_TOOL_PREV_IMAGE:
            self.controller.prev_patch()

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

    def set_brush_radius(self, radius):
        """
        Set the radius of the cursor representing the current brush

        :param radius: The radius to draw the brush at
        :returns: None
        """

        self.logger.debug("Setting brush radius to {}".format(radius))
        self.brush_radius = radius

    def on_left_down(self, event):
        """
        Called when the left mouse button is clicked on the image

        :param event: The mouse event
        :returns: None
        """
        position = self.convert_mouse_to_img_pos(event.GetPosition())

        self.logger.debug("Position {}".format(position))
        self.previous_position = position
        self.controller.handle_left_click(position)

    def on_left_up(self, event):
        """
        Called when the left mouse button is released on the image

        :param event: The mouse event
        :returns: None
        """
        self.logger.debug("left mouse up")
        self.controller.handle_left_release()

    def on_motion(self, event):
        """
        Called when the mouse is moved on the image

        :param event: The mouse event
        :returns: None
        """
        pos = event.GetPosition()
        screen_pos = self.image_panel.GetScreenPosition()
        screen_pos = self.ScreenToClient(screen_pos)

        self.previous_mouse_position = pos

        self.draw_brush(pos)

        if event.Dragging() and event.LeftIsDown():
            current_position = self.convert_mouse_to_img_pos(
                                                        event.GetPosition())

            self.previous_position = current_position
            self.controller.handle_motion(current_position)

    def on_enter_panel(self, event):
        """
        Called when the mouse enters the image panel

        :param event: The mouse event
        :returns: None
        :postcondition: The mouse cursor is removed
        """
        self.logger.debug("Entered Panel")
        cursor = wx.StockCursor(wx.CURSOR_BLANK)
        self.SetCursor(cursor)

    def on_leave_panel(self, event):
        """
        Called when the mouse leaves the image panel

        :param event: The mouse event
        :returns: None
        :postcondition: The mouse cursor is restored to its default icon
        """
        self.logger.debug("Leaving Panel")
        cursor = wx.Cursor(wx.CURSOR_DEFAULT)

    def draw_brush(self, pos=None):
        """
        Draw the brush circle over the image

        :param pos: The position to draw the circle at.
                    The default value is None.
        :returns: None
        """

        if self.current_image is None:
            return

        if pos is None:
            pos = self.previous_mouse_position

        dc = wx.ClientDC(self.image_panel)
        odc = wx.DCOverlay(self.overlay, dc)

        self.show_image(self.current_image, dc)

        if 'wxMac' not in wx.PlatformInfo:
            dc = wx.GCDC(dc)

        dc.SetPen(wx.Pen("black"))
        dc.SetBrush(wx.Brush("blue", wx.TRANSPARENT))
        dc.DrawCircle(pos[0], pos[1], self.brush_radius)

        del odc

    def on_paint(self, event):
        """
        Called when paint events occur

        :param event: The triggering paint event
        :returns: None
        """

        self.logger.debug("Paint")
        dc = wx.ClientDC(self.image_panel)
        odc = wx.DCOverlay(self.overlay, dc)

    def convert_mouse_to_img_pos(self, in_position):
        """
        Convert the mouse event position to an image coordinate

        :param in_position: The position of the mouse event
        :returns: A tuple, the (x,y) position in the image where the event
                  occured
        """

        ctrl_position = self.image_panel.ScreenToClient(in_position)

        screen_position = self.image_panel.GetScreenPosition()

        position_x = ctrl_position[0] + screen_position[0]
        position_y = ctrl_position[1] + screen_position[1]

        return position_x, position_y
