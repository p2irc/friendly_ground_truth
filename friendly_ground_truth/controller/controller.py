"""
File Name: controller.py

Authors: Kyle Seidenthal

Date: 20-02-2020

Description: The main controller for the application

"""

import tkinter.filedialog
import tkinter.messagebox
import logging
import os
import copy

# import matplotlib.pyplot as plt
# import skimage.io as io
import skimage.segmentation as segmentation
# import skimage.color as colour
import numpy as np

from skimage import img_as_ubyte
from friendly_ground_truth.view.tk_view import MainWindow
from friendly_ground_truth.model.model import Image

from enum import Enum

module_logger = logging.getLogger('friendly_gt.controller')


class Mode(Enum):
    """
    Class representing the possible modes for editing

    Attributes:
        THREHSOLD
        ETC
    """
    THRESHOLD = 1
    ADD_REGION = 2
    REMOVE_REGION = 3
    NO_ROOT = 4
    FLOOD_ADD = 6
    FLOOD_REMOVE = 7
    ADD_TIP = 8
    ADD_BRANCH = 9
    ADD_CROSSING = 10
    REMOVE_LANDMARK = 11


class SecondaryMode(Enum):
    """
    Class representing secondary adjustment modes
    """
    ZOOM = 1
    ADJUST_TOOL = 2


class Controller:
    """
    The main controller object for the application

    Attributes:
        stuff
    """
    ZOOM_SCALE = 1.10
    CONTEXT_TRANSPARENCY = 100

    def __init__(self, master):
        """
        Initialize the controller module

        :returns: None
        """
        self.logger = logging.getLogger('friendly_gt.controller.Controller')
        self.logger.debug("Creating controller instance")

        self.current_patch = 0
        self.mask_saved = False

        # Set up the current mode
        self.current_mode = Mode.THRESHOLD
        self.current_secondary_mode = SecondaryMode.ZOOM

        # Whether the preview has been shown
        self.previewed = False

        # Brush radii
        self.add_region_radius = 15
        self.remove_region_radius = 15
        self.add_tip_radius = 2.5
        self.add_branch_radius = 2.5
        self.add_cross_radius = 2.5
        self.remove_landmark_radius = 15

        # Flood Tolerances
        self.flood_add_tolerance = 0.05
        self.flood_remove_tolerance = 0.05

        # Set up the main window
        self.main_window = MainWindow(self, master)

        # Offset of the patch within the context image
        self.patch_offset = (0, 0)

        # Undo Management
        self.undo_manager = UndoManager()

        # Remember chosen directories
        self.last_load_dir = None
        self.last_save_dir = None
        self.image = None

    def load_new_image(self):
        """
        Called when the user wants to load a new image to open a file
        browser dialogue and get the image path

        :returns: None
        """
        self.context_img = None
        self.logger.debug("Opening load file dialog")
        filetypes = [("TIF Files", "*.tif"), ("TIFF Files", "*.tiff"),
                     ("PNG Files", "*.png")]

        if self.last_load_dir is None:
            initial_dir = os.path.expanduser('~')
        else:
            initial_dir = self.last_load_dir

        file_name = tkinter.filedialog.askopenfilename(filetypes=filetypes,
                                                       initialdir=initial_dir)
        if file_name is None:
            return

        self.last_load_dir = os.path.split(file_name)[0]

        self.image_path = file_name
        self.logger.debug("File: {}".format(self.image_path))
        try:
            self.main_window.start_progressbar(Image.NUM_PATCHES ** 2)
            self.image = Image(file_name, self.update_progress_bar)

        except FileNotFoundError:
            self.logger.debug("There was a problem loading the image")
            return

        self.current_patch = 0
        self.display_current_patch()

    def update_progress_bar(self):
        """
        Update the progress bar popup

        :returns: None
        """

        self.main_window.prog_popup.update()
        self.main_window.load_progress += self.main_window.progress_step
        self.main_window.load_prog_var.set(self.main_window.load_progress)

        if self.main_window.load_progress >= Image.NUM_PATCHES ** 2:
            self.main_window.prog_popup.destroy()

    def get_image_name_from_path(self, path):
        """
        Get the filename from the image to use for saving the mask

        Args:
            path: The path to the original image
        Returns:
            The new filename for the mask
        """

        if os.path.isdir(path):
            raise ValueError("Cannot get image name from a directory.")

        basename = os.path.basename(path)
        return os.path.splitext(basename)[0] + '_mask.png'

    def get_landmark_name_from_path(self, path):
        """
        Get the name of the landmark matrix to use for saving

        :param path: The path to the original image
        :returns: The new filename for the mask
        """

        if os.path.isdir(path):
            raise ValueError("Cannot get image name from a directory")

        basename = os.path.basename(path)
        return os.path.splitext(basename)[0] + '_labels.npy'

    def save_mask(self):
        """
        Save the finished image mask

        :returns: None
        """

        if not self.previewed:
            self.show_saved_preview()
            return

        self.mask_saved = True

        if self.last_save_dir is None:
            initial_dir = os.path.expanduser('~')
        else:
            initial_dir = self.last_save_dir

        dir_path = tkinter.filedialog.askdirectory(initialdir=initial_dir)

        self.last_save_dir = dir_path

        self.logger.debug(dir_path)

        if dir_path is None:
            return

        image_name = self.get_image_name_from_path(self.image_path)
        labels_name = self.get_landmark_name_from_path(self.image_path)

        self.mask_pathname = os.path.join(dir_path, image_name)
        self.label_pathname = os.path.join(dir_path, labels_name)

        try:
            self.logger.debug("Saving mask to {}".format(self.mask_pathname))
            self.image.export_mask(self.mask_pathname)
            # self.image.export_labels(self.label_pathname)
            tkinter.messagebox.showinfo("Image Mask Saved!", "Image Mask"
                                        " Saved!")

        except IOError:
            self.logger.error("Could not save file!")
            # TODO: display dialog

    def display_current_patch(self):
        """
        Display the current patch to be displayed

        :returns: None
        """
        if self.image is None:
            return

        patch = self.image.patches[self.current_patch]
        img = self.get_context_patches(patch)

        self.main_window.update_tool = False
        self.main_window.update_thresh_slider_value(patch.thresh)
        self.main_window.update_add_brush_sizer(self.add_region_radius)
        self.main_window.update_remove_brush_sizer(self.remove_region_radius)
        self.main_window.\
            update_flood_add_slider_value(self.flood_add_tolerance)
        self.main_window.\
            update_flood_remove_slider_value(self.flood_remove_tolerance)
        self.main_window.set_brush_radius
        self.main_window.show_image(img)

    def get_context_patches(self, patch):
        """
        Get the patches immediately surrounding the current patch and place
        them in a larger image

        :param patch: The current patch
        :returns: A matrix of patches for display
        """

        # Find the neighbouring patches
        index = patch.patch_index

        if self.context_img is not None:
            patch = self.image.patches[self.current_patch]
            r_start = self.patch_offset[0]
            r_end = r_start + patch.overlay_image.shape[0]
            c_start = self.patch_offset[1]
            c_end = c_start + patch.overlay_image.shape[1]

            o_img = patch.overlay_image
            o_img = np.dstack((o_img, np.full(o_img.shape[0:-1],
                               255, dtype=o_img.dtype)))
            self.logger.debug("Using cached context image")

            self.context_img[r_start:r_end, c_start:c_end] = o_img
            return self.context_img

        neighbouring_indices = []

        start_i = index[0] - 1
        start_j = index[1] - 1

        num_rows = 0
        num_cols = 0

        for i in range(start_i, start_i + 3):

            if i < 0 or i >= self.image.NUM_PATCHES:
                self.logger.debug("Patch Out Of Bounds")
                continue
            for j in range(start_j, start_j + 3):
                if j < 0 or j >= self.image.NUM_PATCHES:
                    self.logger.debug("Patch Out Of Bounds")
                    continue

                neighbouring_indices.append((i, j))

                if num_rows == 0:
                    num_cols += 1
            num_rows += 1

        neighbouring_patches = []
        drawable_patch_index = None  # Index of our patch in this list

        # TODO: This could be more efficient I'm sure
        for i in neighbouring_indices:
            for patch in self.image.patches:
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
                self.patch_offset = (r, c)

            col_num += 1

            if col_num == num_cols:
                col_num = 0
                row_num += 1

            i += 1

        self.context_img = img
        return img

    def convert_click_to_image_position(self, click_location):
        """
        Convert a click location to coordinates in the image

        :param click_location: (x, y) coords of the click
        :returns: The corresponding coordinates in the image
        """
        click_location = (click_location[0] - self.main_window.image_x,
                          click_location[1] - self.main_window.image_y)

        click_location = (click_location[0] / self.main_window.image_scale,
                          click_location[1] / self.main_window.image_scale)

        click_location = (click_location[0] - self.patch_offset[1],
                          click_location[1] - self.patch_offset[0])

        # Make sure we are clicking on the image
        if click_location[0] < 0 or click_location[1] < 0:
            return None

        return click_location

    def next_patch(self):
        """
        Increment the current patch and display it

        :returns: None
        """
        self.context_img = None
        self.undo_manager.clear_undos()

        if self.current_patch < len(self.image.patches)-1:

            self.current_patch += 1
            while self.image.patches[self.current_patch].display is False:
                self.current_patch += 1

            self.display_current_patch()
        else:

            if self.mask_saved:
                return

            self.logger.error("No More Patches")

            dialog_message = "No More Patches - Would you like to save the" \
                             " mask?"

            dialog_title = "No More Patches"

            result = tkinter.messagebox.askyesno(title=dialog_title,
                                                 message=dialog_message)
            self.logger.debug(result)
            if result:
                self.show_saved_preview()

    def show_saved_preview(self):
        """
        Display a preview of the saved mask

        :returns: None
        """
        self.previewed = True
        img = self.image.image
        self.image.create_mask()
        mask = self.image.mask

        overlay = segmentation.mark_boundaries(img, mask)

        overlay = img_as_ubyte(overlay)

        rows = np.any(mask, axis=1)
        cols = np.any(mask, axis=0)
        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]

        overlay = overlay[rmin:rmax, cmin:cmax]

        self.main_window.create_annotation_preview(overlay)

    def prev_patch(self):
        """
        Decrement the current patch and display it

        :returns: None
        """
        self.context_img = None
        self.undo_manager.clear_undos()

        if self.current_patch > 0:

            self.current_patch -= 1
            while self.image.patches[self.current_patch].display is False:
                self.current_patch -= 1

            self.display_current_patch()

        else:
            self.logger.error("No Previous patches")

    def change_mode(self, new_mode_id):
        """
        Change the current editing mode

        :param new_mode_id: The ID of the mode button in the Main Window
        :returns: None
        """
        if new_mode_id != self.main_window.ID_TOOL_NO_ROOT:
            self.main_window.zoom_cursor = False
            self.main_window.flood_cursor = False

        if new_mode_id == self.main_window.ID_TOOL_THRESH:
            self.current_mode = Mode.THRESHOLD
            self.main_window.set_brush_radius(0)
            patch = self.image.patches[self.current_patch]
            self.main_window.update_thresh_slider_value(patch.thresh)

        elif new_mode_id == self.main_window.ID_TOOL_ADD:
            self.current_mode = Mode.ADD_REGION
            self.main_window.set_brush_radius(self.add_region_radius)
            self.main_window.update_add_brush_sizer(self.add_region_radius)

        elif new_mode_id == self.main_window.ID_TOOL_REMOVE:
            self.current_mode = Mode.REMOVE_REGION
            self.main_window.set_brush_radius(self.remove_region_radius)
            self.main_window.\
                update_remove_brush_sizer(self.remove_region_radius)

        elif new_mode_id == self.main_window.ID_TOOL_NO_ROOT:
            self.no_root_activate()

        elif new_mode_id == self.main_window.ID_TOOL_FLOOD_ADD:
            self.current_mode = Mode.FLOOD_ADD
            self.main_window.flood_cursor = True
            self.flood_add_position = None
            # self.flood_add_tolerance = 0.05
            self.main_window.\
                update_flood_add_slider_value(self.flood_add_tolerance)

        elif new_mode_id == self.main_window.ID_TOOL_FLOOD_REMOVE:
            self.current_mode = Mode.FLOOD_REMOVE
            self.main_window.flood_cursor = True
            self.flood_remove_position = None
            # self.flood_remove_tolerance = 0.05
            self.main_window.\
                update_flood_remove_slider_value(self.flood_remove_tolerance)

        elif new_mode_id == self.main_window.ID_TOOL_ADD_TIP:
            self.current_mode = Mode.ADD_TIP
            self.main_window.flood_cursor = True

        elif new_mode_id == self.main_window.ID_TOOL_ADD_BRANCH:
            self.current_mode = Mode.ADD_BRANCH
            self.main_window.flood_cursor = True

        elif new_mode_id == self.main_window.ID_TOOL_ADD_CROSS:
            self.current_mode = Mode.ADD_CROSSING
            self.main_window.flood_cursor = True

        elif new_mode_id == self.main_window.ID_TOOL_REMOVE_LANDMARK:
            self.current_mode = Mode.REMOVE_LANDMARK
            self.main_window.set_brush_radius(self.remove_landmark_radius)

        else:
            self.logger.error("Invalid mode change")

            return False

    def change_secondary_mode(self, new_mode_id):
        """
        Change the secondary mode (for mouse wheel tool adjustments)

        :param new_mode_id: The id of the new mode
        :returns: None
        """

        if new_mode_id == self.main_window.ID_TOOL_ZOOM:
            self.current_secondary_mode = SecondaryMode.ZOOM

        elif new_mode_id == self.main_window.ID_ADJUST_TOOL:
            self.current_secondary_mode = SecondaryMode.ADJUST_TOOL

    def no_root_activate(self):
        """
        Set the mask for the patch to zero, there is no root here

        :returns: None
        """
        patch = self.image.patches[self.current_patch]

        self.undo_manager.add_to_undo_stack(copy.deepcopy(patch), 'no_root')

        patch.clear_mask()
        patch.overlay_mask()

        self.display_current_patch()

    def handle_mouse_wheel(self, wheel_rotation, x, y):
        """
        Handle wheel rotation coming from the mouse

        :param wheel_rotation: The wheel rotation
        :param x: The x-position of the mouse event
        :param y: The y-position of the mouse event
        :returns: True on success, False otherwise
        """

        if self.current_secondary_mode == SecondaryMode.ADJUST_TOOL:
            if self.current_mode == Mode.THRESHOLD:

                self.adjust_threshold(wheel_rotation)

            elif self.current_mode == Mode.ADD_REGION:
                self.adjust_add_region_brush(wheel_rotation)

            elif self.current_mode == Mode.REMOVE_REGION:
                self.adjust_remove_region_brush(wheel_rotation)

            elif self.current_mode == Mode.REMOVE_LANDMARK:
                self.adjust_remove_landmark_brush(wheel_rotation)

            elif self.current_mode == Mode.FLOOD_ADD:
                self.handle_flood_add_tolerance(wheel_rotation)

            elif self.current_mode == Mode.FLOOD_REMOVE:
                self.handle_flood_remove_tolerance(wheel_rotation)
            else:
                return False

        elif self.current_secondary_mode == SecondaryMode.ZOOM:
            self.handle_zoom(wheel_rotation, x, y)

        else:
            self.logger.error("Invalid mouse wheel rotation")
            return False

        return True

    def handle_flood_add_tolerance(self, wheel_rotation):
        """
        Adjust the current tolerance of the flood_add tool

        :param wheel_rotation: The rotation of the mouse wheel
        :returns: None
        """

        if self.flood_add_position is None:
            return

        if wheel_rotation > 0:
            self.flood_add_tolerance += 0.01
        elif wheel_rotation < 0:
            self.flood_add_tolerance -= 0.01

        patch = self.image.patches[self.current_patch]

        patch.flood_add_region(self.flood_add_position,
                               self.flood_add_tolerance)

        patch.overlay_mask()
        self.display_current_patch()

    def set_flood_add_tolerance(self, value):
        """
        Set the current flood add tolerance

        :param value: The value to set it to
        :returns: None
        """

        if self.flood_add_position is None:
            return

        self.flood_add_tolerance = value

        patch = self.image.patches[self.current_patch]

        patch.flood_add_region(self.flood_add_position,
                               self.flood_add_tolerance)

        patch.overlay_mask()
        self.display_current_patch()

    def handle_flood_remove_tolerance(self, wheel_rotation):
        """
        Adjust the current tolerance of the flood_remove tool

        :param wheel_rotation: The rotation of the mouse wheel
        :returns: None
        """

        if self.flood_remove_position is None:
            return

        if wheel_rotation > 0:
            self.flood_remove_tolerance += 0.01
        elif wheel_rotation < 0:
            self.flood_remove_tolerance -= 0.01

        patch = self.image.patches[self.current_patch]

        patch.flood_remove_region(self.flood_remove_position,
                                  self.flood_remove_tolerance)

        patch.overlay_mask()
        self.display_current_patch()

    def set_flood_remove_tolerance(self, value):
        """
        Set the current flood remove tolerance

        :param value: The value to set it to
        :returns: None
        """

        if self.flood_remove_position is None:
            return

        self.flood_remove_tolerance = value

        patch = self.image.patches[self.current_patch]

        patch.flood_remove_region(self.flood_remove_position,
                                  self.flood_remove_tolerance)

        patch.overlay_mask()
        self.display_current_patch()

    def handle_zoom(self, wheel_rotation, x, y):
        """
        Handle zooming with the mouse wheel

        :param wheel_rotation: The roation of the mouse wheel
        :param x: The x-cooridinate
        :param y: The y-coordinate
        :returns: True on success, False otherwise
        """

        old_scale = self.main_window.image_scale

        img_point = (x - self.main_window.image_x,
                     y - self.main_window.image_y)

        img_point = (img_point[0] / self.main_window.image_scale,
                     img_point[1] / self.main_window.image_scale)

        if wheel_rotation > 0 and old_scale < self.main_window.MAX_SCALE:
            self.main_window.image_scale *= self.ZOOM_SCALE
            new_img_point = (img_point[0] * self.ZOOM_SCALE, img_point[1] *
                             self.ZOOM_SCALE)

            translation = (new_img_point[0] - img_point[0],
                           new_img_point[1] - img_point[1])

            self.main_window.image_x -= translation[0]
            self.main_window.image_y -= translation[1]

        elif wheel_rotation < 0 and old_scale > self.main_window.MIN_SCALE:
            self.main_window.image_scale /= self.ZOOM_SCALE
            new_img_point = (img_point[0] / self.ZOOM_SCALE, img_point[1] /
                             self.ZOOM_SCALE)

            translation = (new_img_point[0] - img_point[0],
                           new_img_point[1] - img_point[1])

            self.main_window.image_x -= translation[0]
            self.main_window.image_y -= translation[1]

        else:
            return False

        self.logger.debug("Image Scale: {}".
                          format(self.main_window.image_scale))
        self.display_current_patch()
        return True

    def handle_left_click(self, click_location):
        """
        Handle a left mouse click at the given location

        :param click_location: The location (x, y) of the click
        :returns: True on success, False otherwise
        """

        click_location = self.convert_click_to_image_position(click_location)

        if click_location is None:
            return False

        if self.current_mode == Mode.ADD_REGION:
            self.logger.debug("Add region click {}".format(click_location))

            draw_radius = self.add_region_radius / self.main_window.image_scale

            patch = self.image.patches[self.current_patch]

            self.undo_manager.add_to_undo_stack(copy.deepcopy(patch),
                                                'add_region')

            patch.add_region(click_location, draw_radius)

            self.display_current_patch()

        elif self.current_mode == Mode.REMOVE_REGION:
            self.logger.debug("Remove region click")

            draw_radius = (self.remove_region_radius /
                           self.main_window.image_scale)

            patch = self.image.patches[self.current_patch]

            self.undo_manager.add_to_undo_stack(copy.deepcopy(patch),
                                                'remove_region')

            patch.remove_region(click_location, draw_radius)
            self.display_current_patch()

        elif self.current_mode == Mode.ADD_TIP:

            patch = self.image.patches[self.current_patch]
            patch.add_landmark(click_location, self.add_tip_radius,
                               self.image.TIP_LABEL)
            self.display_current_patch()

        elif self.current_mode == Mode.ADD_CROSSING:
            patch = self.image.patches[self.current_patch]
            patch.add_landmark(click_location, self.add_cross_radius,
                               self.image.CROSS_LABEL)
            self.display_current_patch()

        elif self.current_mode == Mode.ADD_BRANCH:
            patch = self.image.patches[self.current_patch]
            patch.add_landmark(click_location, self.add_branch_radius,
                               self.image.BRANCH_LABEL)
            self.display_current_patch()

        elif self.current_mode == Mode.REMOVE_LANDMARK:
            draw_radius = (self.remove_landmark_radius /
                           self.main_window.image_scale)

            patch = self.image.patches[self.current_patch]
            patch.remove_landmark(click_location, draw_radius)
            self.display_current_patch()

        elif self.current_mode == Mode.FLOOD_ADD:

            patch = self.image.patches[self.current_patch]

            self.undo_manager.add_to_undo_stack(copy.deepcopy(patch),
                                                'flood_add')

            patch.flood_add_region(click_location, self.flood_add_tolerance)

            self.flood_add_position = click_location

            self.display_current_patch()

        elif self.current_mode == Mode.FLOOD_REMOVE:
            patch = self.image.patches[self.current_patch]

            self.undo_manager.add_to_undo_stack(copy.deepcopy(patch),
                                                'flood_remove')

            patch.flood_remove_region(click_location,
                                      self.flood_remove_tolerance)

            self.flood_remove_position = click_location

            self.display_current_patch()

        else:
            return False

        return True

    def handle_right_click(self):
        """
        Called when the right mouse button is clickd

        :returns: None
        """
        self.logger.debug("Right click")

    def handle_left_release(self):
        """
        Handle the release of the left mouse button

        :returns: True on success, False otherwise
        """

        if self.current_mode == Mode.ADD_REGION:
            self.logger.debug("Add region release")
            return True

        elif self.current_mode == Mode.REMOVE_REGION:
            self.logger.debug("Remove region release")
            return True
        else:
            return False

    def handle_motion(self, position):
        """
        Handle motion events of the mouse at the given position

        :param position: The position (x, y) of the mouse during the event
        :returns: True on success, False otherwise
        """
        position = self.convert_click_to_image_position(position)

        if position is None:
            return False

        if self.current_mode == Mode.ADD_REGION:
            self.logger.debug("Adding region")

            draw_radius = self.add_region_radius / self.main_window.image_scale

            patch = self.image.patches[self.current_patch]

            self.undo_manager.add_to_undo_stack(copy.deepcopy(patch),
                                                'add_region_adjust')

            patch.add_region(position, draw_radius)

            self.display_current_patch()

        elif self.current_mode == Mode.REMOVE_REGION:
            self.logger.debug("Removing Region")

            draw_radius = (self.remove_region_radius /
                           self.main_window.image_scale)

            patch = self.image.patches[self.current_patch]

            self.undo_manager.add_to_undo_stack(copy.deepcopy(patch),
                                                'remove_region_adjust')

            patch.remove_region(position, draw_radius)
            self.display_current_patch()

        elif self.current_mode == Mode.REMOVE_LANDMARK:
            draw_radius = (self.remove_landmark_radius /
                           self.main_window.image_scale)

            patch = self.image.patches[self.current_patch]
            patch.remove_landmark(position, draw_radius)
            self.display_current_patch()

        else:
            return False

        return True

    def handle_mouse_wheel_motion(self, position):
        """
        Handle when the mouse wheel is clicked and the mouse is dragged

        :param position: The position of the mouse
        :returns: None
        """

        if self.current_secondary_mode == SecondaryMode.ZOOM:
            self.main_window.image_x += (position[0] -
                                         self.main_window.previous_position[0])

            self.main_window.image_y += (position[1] -
                                         self.main_window.previous_position[1])

            self.display_current_patch()

    def adjust_threshold(self, wheel_rotation):
        """
        Adjust the current threshold of the patch mask

        :param wheel_rotation: The rotation of the mouse wheel
        :returns: None
        """

        patch = self.image.patches[self.current_patch]

        self.undo_manager.add_to_undo_stack(copy.deepcopy(patch),
                                            'threshold_adjust')

        # Adjust the threshold.  Note that it is inverted, because it feels
        # more natural to scroll down to 'reduce' the region, rather than
        # reducing the threshold
        if wheel_rotation > 0 and patch.thresh > 0:
            patch.thresh -= 0.01

        elif wheel_rotation < 0 and patch.thresh < 1:

            patch.thresh += 0.01

        self.main_window.update_thresh_slider_value(patch.thresh)
        self.main_window.update_add_brush_sizer(self.add_region_radius)
        patch.apply_threshold(patch.thresh)
        patch.overlay_mask()

        self.logger.debug("Threshold value: {}".format(patch.thresh))
        self.display_current_patch()

    def set_threshold(self, value):
        """
        Set the value of the threshold

        :param value: Value for the threshold
        :returns: Nonw
        """

        patch = self.image.patches[self.current_patch]

        self.undo_manager.add_to_undo_stack(copy.deepcopy(patch),
                                            'threshold_adjust')

        patch.thresh = value
        patch.apply_threshold(patch.thresh)
        patch.overlay_mask()

        self.display_current_patch()

    def adjust_add_region_brush(self, wheel_rotation):
        """
        Adjust the size of the region brush

        :param wheel_rotation: The rotation of the mouse wheel
        :returns: None
        """

        self.logger.debug("Adjusting add region brush")
        if wheel_rotation > 0:
            self.add_region_radius += 1
        else:
            self.add_region_radius -= 1

        self.main_window.update_add_brush_sizer(self.add_region_radius)
        self.main_window.set_brush_radius(self.add_region_radius)
        self.main_window.draw_brush()

    def set_add_region_brush(self, value):
        """
        Set the value of the add region brush size

        :param value: The size
        :returns: None
        """

        self.add_region_radius = value

        self.main_window.set_brush_radius(self.add_region_radius)
        self.main_window.draw_brush()

    def adjust_remove_landmark_brush(self, wheel_rotation):
        """
        Adjust the size of the remove landmark brush

        :param wheel_rotation: The rotation of the mouse wheel
        :returns: None
        """

        if wheel_rotation > 0:
            self.remove_landmark_radius += 1
        else:
            self.remove_landmark_radius -= 1

        self.main_window.set_brush_radius(self.remove_landmark_radius)
        self.main_window.draw_brush()

    def adjust_remove_region_brush(self, wheel_rotation):
        """
        Adjust the size of the remove region brush

        :param wheel_rotation: the rotation of the mouse wheel
        :returns: None
        """

        self.logger.debug("Adjusting the remove region brush")
        if wheel_rotation > 0:
            self.remove_region_radius += 1
        else:
            self.remove_region_radius -= 1

        self.main_window.update_remove_brush_sizer(self.remove_region_radius)
        self.main_window.set_brush_radius(self.remove_region_radius)
        self.main_window.draw_brush()

    def set_remove_region_brush(self, value):
        """
        Set the value of the remove region brush size

        :param value: The value
        :returns: None
        """
        self.remove_region_radius = value

        self.main_window.set_brush_radius(self.remove_region_radius)
        self.main_window.draw_brush()

    def undo(self):

        patch = self.image.patches[self.current_patch]

        redo_patch, operation = self.undo_manager.undo()

        if redo_patch is None:
            return

        self.undo_manager.add_to_redo_stack(patch, operation)
        self.main_window.toolbar_buttons[self.main_window.ID_TOOL_REDO]\
            .config(state="normal")

        self.image.patches[self.current_patch] = redo_patch

        self.display_current_patch()

    def redo(self):

        patch = self.image.patches[self.current_patch]

        undo_patch, operation = self.undo_manager.redo()

        if undo_patch is None:
            return

        self.undo_manager.add_to_undo_stack(patch, operation)
        if len(self.undo_manager.redo_stack) == 0:
            self.main_window.toolbar_buttons[self.main_window.ID_TOOL_REDO]\
                .config(state="disabled")

        self.image.patches[self.current_patch] = undo_patch

        self.display_current_patch()


class UndoManager():
    """
    Manages Undo Stuff
    """

    MAX_SIZE = 20

    def __init__(self):
        """
        Initialize the Undo Manager

        :returns: None
        """

        self.undo_stack = []
        self.redo_stack = []

    def add_to_undo_stack(self, patch, operation):
        """
        Add the given operation to the undo stack

        :returns: None
        """

        if "threshold_adjust" == operation and len(self.undo_stack) > 0:
            if self.undo_stack[-1][1] == operation:
                return
        elif "adjust" in operation and len(self.undo_stack) > 0:
            if self.undo_stack[-1][1] == operation:
                self.undo_stack.pop()

        self.undo_stack.append((patch, operation))

        if len(self.undo_stack) > self.MAX_SIZE:
            self.undo_stack.pop(0)

    def undo(self):
        """
        Undo the last operation added to the stack

        :returns: The function and its parameters
        """
        try:
            patch, operation = self.undo_stack.pop()
            return patch, operation

        except IndexError:
            return None, None

    def add_to_redo_stack(self, patch, operation):
        """
        Add the given operation to the redo stack

        :returns: None
        """

        self.redo_stack.append((patch, operation))

        if len(self.redo_stack) > self.MAX_SIZE:
            self.redo_stack.pop(0)

    def redo(self):
        """
        Redo the last undone operation

        :returns: The function and its parameters
        """

        try:
            patch, operation = self.redo_stack.pop()
            return patch, operation
        except IndexError:
            return None, None

    def clear_undos(self):

        self.undo_stack = []
        self.redo_stack = []
