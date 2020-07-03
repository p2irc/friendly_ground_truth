"""
File Name: controller.py

Authors: Kyle Seidenthal

Date: 13-05-2020

Description: Main controller for the application

"""
from friendly_ground_truth.view.main_window import MainWindow
from friendly_ground_truth.view.preview_window import PreviewWindow
from friendly_ground_truth.controller.tools import (ThresholdTool,
                                                    AddRegionTool,
                                                    RemoveRegionTool,
                                                    NoRootTool,
                                                    FloodAddTool,
                                                    FloodRemoveTool,
                                                    PreviousPatchTool,
                                                    NextPatchTool,
                                                    UndoTool,
                                                    RedoTool)

from friendly_ground_truth.controller.undo_manager import UndoManager
from friendly_ground_truth.model.model import Image
from friendly_ground_truth.controller.event_logger import EventLogger

# from skimage import segmentation, img_as_ubyte
from skimage.draw import rectangle_perimeter

from sys import platform

import os
import copy
import json
import re

import tkinter.filedialog
import tkinter.messagebox

import numpy as np

import logging
module_logger = logging.getLogger('friendly_gt.controller.controller')


class Controller():
    """
    Main controller for the application.

    Attributes:
        image_tools: A dictionary of tools keyed by their id
    """
    CONTEXT_TRANSPARENCY = 100
    NUM_PATCHES = 10

    DEFAULT_PREFS = {'theme': 'Light'}

    def __init__(self, root):
        """
        Create a Controller object

        Args:
            root: The tk Root

        Returns:
            A controller object

        Postconditions:
            The main application window is started
        """
        # ------------------------------------
        # Private Attributes
        # -----------------------------------

        self.PREFERENCES_PATH = self.get_preferences_path()
        self._grid_img = None
        # The root tkinter object
        self._root = root
        # For logging
        self._logger = logging.getLogger('friendly_gt.controller.'
                                         'controller.Controller')

        self._event_logger = EventLogger()

        # The last directory used to load an image
        self._last_load_dir = None
        # The last directory used to save an image
        self._last_save_dir = None

        self._autosave_dir = None

        # Image containing neighbouring patches
        self._context_img = None

        # For managing undo operations
        self._undo_manager = UndoManager()
        # A dictionary of image tools
        self._image_tools = {}
        self._init_tools()

        # Initialize the main window
        self._main_window = MainWindow(self._root, self)

        # The path to the current image
        self._image_path = None

        # The current image
        self._image = None

        # The index of the current patch in _image.patches
        self._current_patch_index = 0

        # Whether the mask has been saved
        self._mask_saved = False

        # The current tool in use
        self._current_tool = None

        # The offset of the current patch within the context image
        self._patch_offset = (0, 0)

        # Whether the mask preview has been shown or not
        self._previewed = False

        # Disable the redo button for now
        self._main_window.disable_button(self._redo_id)
        self._main_window.disable_button(self._undo_id)

        self._ask_save_dir()

    @property
    def image_tools(self):
        """
        A dictionary of available tools for annotating the image with.
        """
        return self._image_tools

    # ===================================================
    # PUBLIC FUNCTIONS
    # ===================================================
    def get_preferences_path(self):
        """
        Return the path to the preferences file.


        Returns:
            The path to the preferences file.
        """
        if platform != 'win32':

            home = os.path.expanduser("~")
            data_dir = os.path.join(home, ".friendly_ground_truth/")

            if not os.path.exists(data_dir):
                os.mkdir(data_dir)

            preferences_path = os.path.join(data_dir,
                                            "user_preferences.json")

        else:
            preferences_path = "./user_preferences.json"

        return preferences_path

    def load_existing_mask(self):
        """
        Load in an existing annotation mask.


        Returns:
            None
        """
        if self._image is None:
            tkinter.messagebox.showinfo("No Image Loaded",
                                        "You must load an image before "
                                        " loading an existing mask!")

            return



        self._context_img = None
        self._grid_img = None

        filetypes = [("PNG Files", "*.png"), ("JPEG Files", "*.jpg")]

        if self._last_load_dir is None:
            initial_dir = os.path.expanduser("~")
        else:
            initial_dir = self._last_load_dir

        file_name = tkinter.filedialog.askopenfilename(filetypes=filetypes,
                                                       initialdir=initial_dir)

        self._logger.debug("Selected mask: {}".format(file_name)
                )
        # Make sure the names are similar
        mask_filename = os.path.split(file_name)[-1]

        image_filename = \
            os.path.splitext(os.path.split(self._image_path)[-1])[0]

        if image_filename not in mask_filename:
            tkinter.messagebox.showinfo("Invalid Mask",
                                        "The name of the mask you have chosen"
                                        " does not match the name of the "
                                        "loaded image.")

            return

        if file_name is None or file_name == ():
            return

        try:
            self._main_window.start_progressbar(self.NUM_PATCHES ** 2)


            self._image.load_mask(file_name)

        except FileNotFoundError:
            self._logger.exception("There was a problem loading the image.")
            return

        image_shape = self._image.image.shape
        patch_grid_shape = self._image.patches[0].patch.shape

        self._event_logger.log_load_mask(image_filename, image_shape[1],
                                         image_shape[0], patch_grid_shape[1],
                                         patch_grid_shape[0])

        self._current_patch_index = 0

        self._logger.debug("Displaying patch.")
        self._display_current_patch(new=True)

        self.activate_tool(self._default_tool)
        self._main_window.set_default_tool(self._default_tool)

    def load_new_image(self):
        """
        Load a new image with a file dialog.


        Returns:
            None
        """

        self._context_img = None
        self._grid_img = None
        self._event_logger.active_tool = "None"

        filetypes = [("TIF Files", "*.tif"), ("TIFF Files", "*.tiff"),
                     ("PNG Files", "*.png"), ("JPEG Files", "*.jpg")]

        if self._last_load_dir is None:
            initial_dir = os.path.expanduser("~")
        else:
            initial_dir = self._last_load_dir

        file_name = tkinter.filedialog.askopenfilename(filetypes=filetypes,
                                                       initialdir=initial_dir)

        if file_name is None or file_name == ():
            return

        self._last_load_dir = os.path.split(file_name)[0]

        self._image_path = file_name

        try:
            self._main_window.start_progressbar(self.NUM_PATCHES ** 2)

            del self._image
            self._image = Image(file_name, 10, self._update_progressbar)

        except FileNotFoundError:
            self._logger.exception("There was a problem loading the image.")
            return

        image_filename = os.path.split(file_name)[-1]
        image_shape = self._image.image.shape
        patch_grid_shape = self._image.patches[0].patch.shape

        self._event_logger.log_load_image(image_filename, image_shape[1],
                                          image_shape[0], patch_grid_shape[1],
                                          patch_grid_shape[0])

        self._current_patch_index = 0

        self._display_current_patch(new=True)
        self._main_window.update_image_indicator(self._image_path)

        self.activate_tool(self._default_tool)
        self._main_window.set_default_tool(self._default_tool)

    def save_mask(self):
        """
        Save the finished image mask.


        Returns:
            None
        """

        if self._image is None:
            return

        self._mask_saved = True

        if self._last_save_dir is None:
            initial_dir = os.path.expanduser("~")
        else:
            initial_dir = self._last_save_dir

        dir_path = tkinter.filedialog.askdirectory(initialdir=initial_dir)

        if dir_path is None:
            return

        self._last_save_dir = dir_path

        image_name = self._get_image_name_from_path(self._image_path)
        # labels_name = self._get_landmark_name_from_path(self._image_path)

        mask_pathname = os.path.join(dir_path, image_name)
        # label_pathname = os.path.join(dir_path, labels_name)

        try:
            self._image.export_mask(mask_pathname)
            # self._image.export_labels(label_pathname)

            tkinter.messagebox.showinfo("Image Mask Saved!",
                                        "Image Mask Saved!")
        except IOError:
            self._logger.error("Could not save file!")

        self._previewed = False

    def set_preferences(self, preferences):
        """
        Set the current preferences for the application.

        Args:
            preferences: A dictionary of preferences and their values.

        Returns:
            None
        """
        theme = preferences['theme']

        self._main_window.set_theme(theme)

    def load_preferences(self):
        """
        Load the preferences saved in the preferences file.


        Returns:
            A dictionary containing the user's preferences.
        """
        if not os.path.exists(self.PREFERENCES_PATH):
            return self.DEFAULT_PREFS

        with open(self.PREFERENCES_PATH, 'r') as fin:
            preferences = json.load(fin)

        return preferences

    def save_preferences(self, preferences):
        """
        Save the user preferences.

        Args:
            preferences: A dictionary containing the user preferences.

        Returns:
            None
        """

        with open(self.PREFERENCES_PATH, 'w') as fout:
            json.dump(preferences, fout)

    def activate_tool(self, id):
        """
        Activate the given tool id.

        Args:
            id: The id of the tool.

        Returns:
            None

        Postcondition:
            The current tool is set to the tool matching the id
            Any activation functionality of the tool is performed.
        """
        if self._image is None:
            return

        tool = self.image_tools[id]
        tool.image = self._image
        tool.patch = self._image.patches[self._current_patch_index]

        old_tool = None

        if not tool.persistant:
            old_tool = self._current_tool
        else:
            self._event_logger.active_tool = tool.name

        self._current_tool = tool

        tool.on_activate(self._current_patch_index)

        if old_tool is not None:
            self._current_tool = old_tool
            tool = old_tool

        tool.lock_undos()
        # self._display_current_patch()
        self._main_window.update_info_panel(tool)
        self._main_window.set_canvas_cursor(tool.cursor)
        tool.unlock_undos()

        if not self._undo_manager.undo_empty:
            self._main_window.enable_button(self._undo_id)

    def adjust_tool(self, direction):
        """
        Adjust the current tool.

        Args:
            direction: An integer, positive is up, negative is down.

        Returns:
            None

        Postconditions:
            The current tool's adjust tool function is called.
        """
        self._current_tool.on_adjust(direction)
        # self._display_current_patch()

        if not self._undo_manager.undo_empty:
            self._main_window.enable_button(self._undo_id)

    def click_event(self, pos):
        """
        A click event in the main window has occured.

        Args:
            pos: The position of the event.

        Returns:
            None

        Postconditions:
            The current tool's on_click() function is called.
        """
        # Correct for offset in context image
        pos = pos[0] - self._patch_offset[1], pos[1] - self._patch_offset[0]

        # Need to invert the position, because tkinter coords are backward from
        # skimage
        pos = round(pos[1]-1), round(pos[0]-1)

        self._logger.debug("Click Event: {}".format(pos))

        if self._current_tool is not None:
            self._current_tool.on_click(pos)

        if not self._undo_manager.undo_empty:
            self._main_window.enable_button(self._undo_id)

    def drag_event(self, pos, drag_id=None):
        """
        A click event in the main window has occured.

        Args:
            pos: The position of the event.
            drag_id: Unique identifier for the drag event.

        Returns:
            None

        Postconditions:
            The current tool's on_drag() function is called.
        """
        # Correct for offset in context image
        pos = pos[0] - self._patch_offset[1], pos[1] - self._patch_offset[0]

        # Need to invert the position, because tkinter coords are backward from
        # skimage
        pos = round(pos[1]-1), round(pos[0]-1)

        self._current_tool.on_drag(pos, drag_id=drag_id)

        if not self._undo_manager.undo_empty:
            self._main_window.enable_button(self._undo_id)

    def navigate_to_patch(self, pos):
        """
        Navigate to the patch containing the given coordinates in the original
        image.

        Args:
            pos: The position in the image to go to.

        Returns:
            None
        """

        pos = (pos[1], pos[0])

        patch_index = self._image.get_patch_from_coords(pos)

        patch = self._image.patches[patch_index]

        self._next_patch_callback(patch, patch_index)

    def log_mouse_event(self, pos, event, button):
        """
        Add a mouse event to the event log.

        Args:
            pos: The position of the mouse event.
            event: The type of event: 'click', 'release'
            button: The mouse button used for the event.

        Returns:
            None
        """

        patch_pos = self._convert_canvas_to_patch_pos(pos)

        patch_shape = self.\
            _image.patches[self._current_patch_index].patch.shape

        if patch_pos[0] < 0 or patch_pos[0] > patch_shape[0]:
            return

        if patch_pos[1] < 0 or patch_pos[1] > patch_shape[1]:
            return

        image_pos = self._convert_patch_to_image_pos(patch_pos)

        patch_grid_coord = self.\
            _image.patches[self._current_patch_index].patch_index

        if event == "release":

            self._event_logger.log_event("mouse_up", patch_grid_coord,
                                         patch_coord=patch_pos,
                                         image_coord=image_pos,
                                         mouse_button=button)
        elif event == "click":
            self._event_logger.log_event("mouse_down", patch_grid_coord,
                                         patch_coord=patch_pos,
                                         image_coord=image_pos,
                                         mouse_button=button)

    def log_zoom_event(self, zoom_factor):
        """
        Add a zoom event to the event log.

        Args:
            zoom_factor: The new zoom factor.

        Returns:
            None
        """

        patch_grid_coord = self.\
            _image.patches[self._current_patch_index].patch_index

        self._event_logger.log_event("zoom_factor_change", patch_grid_coord,
                                     new_zoom_factor=zoom_factor)

    def log_drag_event(self, drag_type, start, end):
        """
        Add a mouse drag event to the event log.

        Args:
            drag_type: The type of drag: 'brush', 'pan'.
            start: The starting position of the drag.
            end: The end position of the drag.

        Returns:
            None
        """

        patch_grid_coord = self.\
            _image.patches[self._current_patch_index].patch_index

        start = self._convert_canvas_to_patch_pos(start)
        end = self._convert_canvas_to_patch_pos(end)

        image_start = self._convert_patch_to_image_pos(start)
        image_end = self._convert_patch_to_image_pos(end)

        self._event_logger.log_event("drag", patch_grid_coord,
                                     patch_start=start, patch_end=end,
                                     image_start=image_start,
                                     image_end=image_end,
                                     drag_type=drag_type)

    # ===================================================
    # Private Functions
    # ===================================================

    def _ask_save_dir(self):
        """
        Ask the user for a directory to save files in.


        Returns:
            None

        Postconditions:
            A file selection dialog will be presented.
        """

        # Get the chosen directory
        if self._last_save_dir is None:
            initial_dir = os.path.expanduser("~")
        else:
            initial_dir = self._last_save_dir

        dir_path = tkinter.filedialog.askdirectory(initialdir=initial_dir,
                                                   title="Choose Output"
                                                   " Directory")
        if dir_path is None:
            self._ask_save_dir()

        self._last_save_dir = dir_path

        self._autosave_dir = dir_path

        # Get annotation group id

        # For our purposes, the folder structure is:
        # annoations-xxx-xx/annoations
        folder = os.path.split(dir_path)[0]
        folder = os.path.split(folder)[-1]

        pattern = re.compile("^annotations-[0-9][0-9][0-9]-[0-9]+")

        if pattern.match(folder):
            log_name = folder + ".log"

        else:
            log_name = 'events.log'

        log_name = os.path.join(self._autosave_dir, log_name)

        fh = logging.FileHandler(log_name)
        fh.setLevel(logging.INFO)

        event_format = '%(message)s'
        event_formatter = logging.Formatter(event_format)
        fh.setFormatter(event_formatter)

        self._event_logger.add_handler(fh)

    def _convert_canvas_to_patch_pos(self, pos):
        """
        Convert the givent canvas coordinate to a patch-relative coordinate.

        Args:
            pos: The position to convert.

        Returns:
            The coordinate converted to a patch-releative coordinate.
        """

        # Correct for offset in context image
        pos = pos[0] - self._patch_offset[1], pos[1] - self._patch_offset[0]

        # Need to invert the position, because tkinter coords are backward from
        # skimage
        pos = round(pos[1]-1), round(pos[0]-1)

        return pos

    def _convert_patch_to_image_pos(self, pos):
        """
        Convert a patch coordinate to an image-relative coordinate.

        Args:
            pos: The patch position to convert.

        Returns:
            The coordinate relative to the whole image.
        """

        # TODO: Fix private variable
        block_size = self._image._block_size

        patch_grid_coord = self.\
            _image.patches[self._current_patch_index].patch_index

        image_x = block_size[1] * (patch_grid_coord[1]) + pos[1]
        image_y = block_size[0] * (patch_grid_coord[0]) + pos[0]

        return image_y, image_x

    def _init_tools(self):
        """
        Create all the required tools.


        Returns:
            None

        Postconditions:
            self._image_tools will be created as a dictionary of id, tool pairs
        """

        image_tools = {}

        thresh_tool = ThresholdTool(self._undo_manager,
                                    event_logger=self._event_logger)
        image_tools[thresh_tool.id] = thresh_tool

        self._default_tool = thresh_tool.id

        add_reg_tool = AddRegionTool(self._undo_manager,
                                     event_logger=self._event_logger)

        add_reg_tool.bind_brush(self._brush_size_callback)

        image_tools[add_reg_tool.id] = add_reg_tool

        rem_reg_tool = RemoveRegionTool(self._undo_manager,
                                        event_logger=self._event_logger)

        rem_reg_tool.bind_brush(self._brush_size_callback)
        image_tools[rem_reg_tool.id] = rem_reg_tool

        flood_add_tool = FloodAddTool(self._undo_manager,
                                      event_logger=self._event_logger)

        image_tools[flood_add_tool.id] = flood_add_tool

        flood_rem_tool = FloodRemoveTool(self._undo_manager,
                                         event_logger=self._event_logger)

        image_tools[flood_rem_tool.id] = flood_rem_tool

        no_root_tool = NoRootTool(self._undo_manager,
                                  self._next_patch_callback,
                                  event_logger=self._event_logger)

        image_tools[no_root_tool.id] = no_root_tool

        prev_patch_tool = PreviousPatchTool(self._undo_manager,
                                            self._prev_patch_callback,
                                            event_logger=self._event_logger)

        image_tools[prev_patch_tool.id] = prev_patch_tool

        next_patch_tool = NextPatchTool(self._undo_manager,
                                        self._next_patch_callback,
                                        event_logger=self._event_logger)

        image_tools[next_patch_tool.id] = next_patch_tool

        undo_tool = UndoTool(self._undo_manager,
                             self._undo_callback,
                             event_logger=self._event_logger)

        image_tools[undo_tool.id] = undo_tool
        self._undo_id = undo_tool.id

        redo_tool = RedoTool(self._undo_manager,
                             self._redo_callback,
                             event_logger=self._event_logger)

        image_tools[redo_tool.id] = redo_tool
        self._redo_id = redo_tool.id

        for id in image_tools.keys():
            image_tools[id].bind_to(self._display_current_patch)

        self._image_tools = image_tools

    def _next_patch_callback(self, patch, index):
        """
        Called when the next patch is determined.

        Args:
            patch: The next patch.
            index: The index in the patches list of the patch.

        Returns:
            None
        """
        self._logger.debug("Next patch {}.".format(index))

        if patch is None or index == -1:
            self._display_current_patch()

            tkinter.messagebox.showinfo("No More Patches",
                                        "There are no patches left in the "
                                        "image.  You can save the mask using "
                                        "the file menu, or use the "
                                        "preview window to review "
                                        "your mask.")

            self._display_current_patch()
            return

        cur_patch = self._image.patches[self._current_patch_index]
        cur_patch.undo_history = copy.deepcopy(self._undo_manager)

        self._context_img = None
        self._current_patch_index = index

        cur_patch = self._image.patches[self._current_patch_index]

        if cur_patch.undo_history is None:
            self._undo_manager = UndoManager()
        else:
            self._undo_manager = copy.deepcopy(cur_patch.undo_history)

        for key in self._image_tools.keys():
            self._image_tools[key].patch = patch
            self._image_tools[key].undo_manager = self._undo_manager

        self._display_current_patch(new=True)

        if self._undo_manager.undo_empty:
            self._main_window.disable_button(self._undo_id)
        else:
            self._main_window.enable_button(self._undo_id)

        if self._undo_manager.redo_empty:
            self._main_window.disable_button(self._redo_id)
        else:
            self._main_window.enable_button(self._redo_id)

    def _prev_patch_callback(self, patch, index):
        """
        Called when the previous patch is determined.

        Args:
            patch: The previous patch
            index: The index of that patch in the list of patches.

        Returns:
            None
        """

        if patch is None or index == -1:
            return

        cur_patch = self._image.patches[self._current_patch_index]
        cur_patch.undo_history = copy.deepcopy(self._undo_manager)

        self._context_img = None
        self._current_patch_index = index

        cur_patch = self._image.patches[self._current_patch_index]

        if cur_patch.undo_history is None:
            self._undo_manager = UndoManager()
        else:
            self._undo_manager = copy.deepcopy(cur_patch.undo_history)

        for key in self._image_tools.keys():
            self._image_tools[key].patch = patch
            self._image_tools[key].undo_manager = self._undo_manager

        self._display_current_patch(new=True)

        self._main_window.disable_button(self._undo_id)
        self._main_window.disable_button(self._redo_id)

    def _undo_callback(self, patch, string):
        """
        Called when undo is done.

        Args:
            patch: The patch returned from the undo stack.
            string: The string for that patch.

        Returns:
            None
        """
        if patch is None:
            return

        current_patch = self._image.patches[self._current_patch_index]

        self._undo_manager.add_to_redo_stack(copy.deepcopy(current_patch),
                                             string)

        self._main_window.enable_button(self._redo_id)

        if self._undo_manager.undo_empty:
            self._main_window.disable_button(self._undo_id)

        self._image.patches[self._current_patch_index] = patch

        for key in self._image_tools.keys():
            self._image_tools[key].lock_undos()
            self._image_tools[key].patch = patch

    def _redo_callback(self, patch, string):
        """
        Called when redo is done.

        Args:
            patch: The patch returned from the redo stack.
            string: The string for that patch.

        Returns:
            None
        """
        if patch is None:
            return

        current_patch = self._image.patches[self._current_patch_index]

        self._undo_manager.add_to_undo_stack(copy.deepcopy(current_patch),
                                             string)

        if self._undo_manager.redo_empty:
            self._main_window.disable_button(self._redo_id)

        self._main_window.enable_button(self._undo_id)

        self._image.patches[self._current_patch_index] = patch

        for key in self._image_tools.keys():
            self._image_tools[key].lock_undos()
            self._image_tools[key].patch = patch

    def _display_current_patch(self, new=False):
        """
        Display the current patch.


        Returns:
            None

        Postconditions:
            The main window's canvas will display the given image.
        """
        if self._image is None:
            self._logger.debug("No Image to Display!")
            return

        patch = self._image.patches[self._current_patch_index]
        img = self._get_context_patches(patch)

        self._main_window.show_image(img, new=new,
                                     patch_offset=self._patch_offset)

        if self._current_tool is not None:
            self._current_tool.unlock_undos()
        if self._undo_manager.undo_empty:
            self._main_window.disable_button(self._undo_id)
        else:
            self._main_window.enable_button(self._undo_id)

    def _brush_size_callback(self, radius):
        """
        Called when a brush tool is updated.

        Args:
            radius: The new brush radius.

        Returns:
            None
        """
        self._main_window.set_canvas_brush_size(radius)

    def _get_context_patches(self, patch):
        """
        Get the patches immediately surrounding the current patch and place
        them in a larger image.

        Args:
            patch: The current patch

        Returns:
            An image for display.
        """

        # Find the neighbouring patches
        index = patch.patch_index

        if self._context_img is not None:
            patch = self._image.patches[self._current_patch_index]
            r_start = self._patch_offset[0]
            r_end = r_start + patch.overlay_image.shape[0]
            c_start = self._patch_offset[1]
            c_end = c_start + patch.overlay_image.shape[1]

            o_img = patch.overlay_image
            o_img = np.dstack((o_img, np.full(o_img.shape[0:-1],
                               255, dtype=o_img.dtype)))

            self._context_img[r_start:r_end, c_start:c_end] = o_img
            return self._context_img

        neighbouring_indices = []

        start_i = index[0] - 1
        start_j = index[1] - 1

        num_rows = 0
        num_cols = 0

        for i in range(start_i, start_i + 3):

            if i < 0 or i >= self._image.num_patches:
                continue
            for j in range(start_j, start_j + 3):
                if j < 0 or j >= self._image.num_patches:
                    continue

                neighbouring_indices.append((i, j))

                if num_rows == 0:
                    num_cols += 1
            num_rows += 1

        neighbouring_patches = []
        drawable_patch_index = None  # Index of our patch in this list

        # TODO: This could be more efficient I'm sure
        for i in neighbouring_indices:
            for patch in self._image.patches:
                if patch.patch_index == i:
                    o_img = patch.overlay_image

                    if i == index:
                        o_img = np.dstack((o_img, np.full(o_img.shape[0:-1],
                                           255,
                                           dtype=o_img.dtype)))
                        drawable_patch_index = neighbouring_indices.index(i)
                    else:
                        o_img = np.dstack((o_img, np.full(o_img.shape[0:-1],
                                           self.CONTEXT_TRANSPARENCY,
                                           dtype=o_img.dtype)))

                    neighbouring_patches.append(o_img)

        # Layer them into a numpy array
        img_shape = (patch.overlay_image.shape[0] * num_rows,
                     patch.overlay_image.shape[1] * num_cols, 4)
        img = np.zeros(img_shape, dtype=np.ubyte)

        col_num = 0
        row_num = 0

        i = 0
        for patch in neighbouring_patches:
            r, c = row_num, col_num
            r = r * patch.shape[0]
            c = c * patch.shape[1]
            img[r:r+patch.shape[0],
                c:c+patch.shape[1]] += patch
            if i == drawable_patch_index:
                self._patch_offset = (r, c)

            col_num += 1

            if col_num == num_cols:
                col_num = 0
                row_num += 1

            i += 1

        self._context_img = img
        return img

    def _update_progressbar(self):
        """
        Update the progressbar popup


        Returns:
            None

        Postconditions:
            The progressbar will be incremented.
        """
        self._main_window.progress_popup.update()
        self._main_window.load_progress += self._main_window.progress_step
        self._main_window.load_progress_var\
            .set(self._main_window.load_progress)

        if self._main_window.load_progress >= self.NUM_PATCHES ** 2:
            self._main_window.progress_popup.destroy()

    def show_saved_preview(self):
        """
        Display a preview of the saved mask overlaid with the image.


        Returns:
            None

        Postconditions:
            A window displaying the image and mask is shown.
        """

        overlay = self._image.create_overlay_img()

        PreviewWindow(overlay, self, self._main_window.style)

    def get_image_preview(self):
        """
        Get a preview of the image mask.


        Returns:
            An image representing the preview of the mask.
        """

        img = self._image.create_overlay_img()

        patch_size_x = self\
            ._image.patches[self._current_patch_index].patch.shape[0]

        patch_size_y = self\
            ._image.patches[self._current_patch_index].patch.shape[1]

        # Draw patch grid
        if self._grid_img is None:
            self._grid_img = np.zeros(img.shape, dtype=np.bool)

            for i in range(self.NUM_PATCHES):
                for j in range(self.NUM_PATCHES):
                    start_x = i * patch_size_x
                    stop_x = start_x + patch_size_x

                    start_y = j * patch_size_y
                    stop_y = start_y + patch_size_y

                    rec_start = (start_x, start_y)
                    rec_end = (stop_x, stop_y)

                    rr, cc = rectangle_perimeter(rec_start, end=rec_end,
                                                 shape=self._grid_img.shape)

                    self._grid_img[rr, cc] = True

        img[self._grid_img] = 207

        # Draw current Patch
        start_x = self._image\
            .patches[self._current_patch_index].patch_index[0] * patch_size_x

        stop_x = start_x + patch_size_x

        start_y = self\
            ._image.patches[self._current_patch_index]\
            .patch_index[1] * patch_size_y

        stop_y = start_y + patch_size_y

        rec_start = (start_x, start_y)
        rec_end = (stop_x, stop_y)

        rr, cc = rectangle_perimeter(rec_start, end=rec_end,
                                     shape=self._image.image.shape)

        img[rr, cc] = [255, 255, 0]

        for i in range(4):
            rec_start = (rec_start[0] + 1, rec_start[1] + 1)
            rec_end = (rec_end[0] - 1, rec_end[1] - 1)

            rr, cc = rectangle_perimeter(rec_start, end=rec_end,
                                         shape=self._image.image.shape)

            img[rr, cc] = [255, 255, 0]

        return img

    def _get_image_name_from_path(self, path):
        """
        Get the name of the image from its original path.

        Args:
            path: The path to the original image.

        Returns:
            The name to save the image mask as.
        """
        if os.path.isdir(path):
            raise ValueError("Cannot get image name from a directory.")

        basename = os.path.basename(path)

        return os.path.splitext(basename)[0] + '_mask.png'
