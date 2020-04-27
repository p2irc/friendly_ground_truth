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

import matplotlib.pyplot as plt
import skimage.io as io
import skimage.segmentation as segmentation
import skimage.color as colour
import numpy as np

from friendly_ground_truth.view.tk_view import MainWindow
from friendly_ground_truth.model.model import Image

from enum import Enum

module_logger = logging.getLogger('friendly_gt.controller')


class Mode(Enum):
    """
    Class representing the possible modes for editing
    """
    THRESHOLD = 1
    ADD_REGION = 2
    REMOVE_REGION = 3
    NO_ROOT = 4
    ZOOM = 5
    FLOOD_ADD = 6
    FLOOD_REMOVE = 7
    ADD_TIP = 8
    ADD_BRANCH = 9
    ADD_CROSSING = 10
    REMOVE_LANDMARK = 11


class Controller:
    """
    The main controller object for the application
    """

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

    def load_new_image(self):
        """
        Called when the user wants to load a new image to open a file
        browser dialogue and get the image path

        :returns: None
        """
        self.logger.debug("Opening load file dialog")
        filetypes = [("TIF Files", "*.tif"), ("TIFF Files", "*.tiff"),
                     ("PNG Files", "*.png")]
        file_name = tkinter.filedialog.askopenfilename(filetypes=filetypes)

        if file_name is None:
            return

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

        :param path: The path to the original image
        :returns: The new filename for the mask
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
        dir_path = tkinter.filedialog.askdirectory()
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
            self.image.export_labels(self.label_pathname)

        except IOError:
            self.logger.error("Could not save file!")
            # TODO: display dialog

    def display_current_patch(self):
        """
        Display the current patch to be displayed

        :returns: None
        """

        patch = self.image.patches[self.current_patch]

        self.main_window.show_image(patch.overlay_image)

    def next_patch(self):
        """
        Increment the current patch and display it

        :returns: None
        """

        if self.current_patch < len(self.image.patches)-1:

            self.current_patch += 1
            while self.image.patches[self.current_patch].display is False:
                self.current_patch += 1

            self.main_window.image_scale = 1
            self.main_window.image_x = 0
            self.main_window.image_y = 0

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
                self.save_mask()
                self.mask_saved = True

                tkinter.messagebox.showinfo("Image Mask Saved!", "Image Mask"
                                            " Saved!")

            self.show_saved_preview()

    def show_saved_preview(self):
        """
        Display a preview of the saved mask

        :returns: None
        """

        img = io.imread(self.image_path)
        landmarks = np.load(self.label_pathname)
        mask = io.imread(self.mask_pathname)

        rows = np.any(mask, axis=1)
        cols = np.any(mask, axis=0)
        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]

        overlay_img = colour.label2rgb(landmarks, img, bg_label=0,
                                       colors=['red', 'green', 'blue'])

        boundary_img = segmentation.mark_boundaries(overlay_img, mask)

        boundary_img = boundary_img[rmin:rmax, cmin:cmax]

        plt.imshow(boundary_img)
        plt.show()

    def prev_patch(self):
        """
        Decrement the current patch and display it

        :returns: None
        """

        if self.current_patch > 0:

            self.current_patch -= 1
            while self.image.patches[self.current_patch].display is False:
                self.current_patch -= 1

            self.main_window.image_scale = 1
            self.main_window.image_x = 0
            self.main_window.image_y = 0

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

        elif new_mode_id == self.main_window.ID_TOOL_ADD:
            self.current_mode = Mode.ADD_REGION
            self.main_window.set_brush_radius(self.add_region_radius)

        elif new_mode_id == self.main_window.ID_TOOL_REMOVE:
            self.current_mode = Mode.REMOVE_REGION
            self.main_window.set_brush_radius(self.remove_region_radius)

        elif new_mode_id == self.main_window.ID_TOOL_NO_ROOT:
            self.no_root_activate()

        elif new_mode_id == self.main_window.ID_TOOL_ZOOM:
            self.current_mode = Mode.ZOOM
            self.main_window.set_brush_radius(0)
            self.main_window.zoom_cursor = True

        elif new_mode_id == self.main_window.ID_TOOL_FLOOD_ADD:
            self.current_mode = Mode.FLOOD_ADD
            self.main_window.flood_cursor = True
            self.flood_add_position = None
            self.flood_add_tolerance = 0.05

        elif new_mode_id == self.main_window.ID_TOOL_FLOOD_REMOVE:
            self.current_mode = Mode.FLOOD_REMOVE
            self.main_window.flood_cursor = True
            self.flood_remove_position = None
            self.flood_remove_tolerance = 0.05

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

    def no_root_activate(self):
        """
        Set the mask for the patch to zero, there is no root here

        :returns: None
        """

        patch = self.image.patches[self.current_patch]
        patch.clear_mask()
        patch.overlay_mask()

        self.display_current_patch()

    def handle_mouse_wheel(self, wheel_rotation):
        """
        Handle wheel rotation coming from the mouse

        :param wheel_rotation: The wheel rotation
        :returns: True on success, False otherwise
        """

        if self.current_mode == Mode.THRESHOLD:

            self.adjust_threshold(wheel_rotation)

        elif self.current_mode == Mode.ADD_REGION:
            self.adjust_add_region_brush(wheel_rotation)

        elif self.current_mode == Mode.REMOVE_REGION:
            self.adjust_remove_region_brush(wheel_rotation)

        elif self.current_mode == Mode.REMOVE_LANDMARK:
            self.adjust_remove_landmark_brush(wheel_rotation)

        elif self.current_mode == Mode.ZOOM:
            self.handle_zoom(wheel_rotation)

        elif self.current_mode == Mode.FLOOD_ADD:
            self.handle_flood_add_tolerance(wheel_rotation)

        elif self.current_mode == Mode.FLOOD_REMOVE:
            self.handle_flood_remove_tolerance(wheel_rotation)

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

    def handle_zoom(self, wheel_rotation):
        """
        Handle zooming with the mouse wheel

        :param wheel_rotation: The roation of the mouse wheel
        :returns: True on success, False otherwise
        """

        old_scale = self.main_window.image_scale

        if wheel_rotation > 0 and old_scale < self.main_window.MAX_SCALE:
            self.main_window.image_scale *= 2.0

        elif wheel_rotation < 0 and old_scale > self.main_window.MIN_SCALE:
            self.main_window.image_scale /= 2.0

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

        click_location = (click_location[0] - self.main_window.image_x,
                          click_location[1] - self.main_window.image_y)

        click_location = (click_location[0] / self.main_window.image_scale,
                          click_location[1] / self.main_window.image_scale)

        if self.current_mode == Mode.ADD_REGION:
            self.logger.debug("Add region click")

            draw_radius = self.add_region_radius / self.main_window.image_scale

            patch = self.image.patches[self.current_patch]
            patch.add_region(click_location, draw_radius)

            self.display_current_patch()

        elif self.current_mode == Mode.REMOVE_REGION:
            self.logger.debug("Remove region click")

            draw_radius = (self.remove_region_radius /
                           self.main_window.image_scale)

            patch = self.image.patches[self.current_patch]
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

            patch.flood_add_region(click_location, self.flood_add_tolerance)

            self.flood_add_position = click_location

            self.display_current_patch()

        elif self.current_mode == Mode.FLOOD_REMOVE:
            patch = self.image.patches[self.current_patch]

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
        # Reset zoom
        if self.current_mode == Mode.ZOOM:
            self.main_window.image_x = 0
            self.main_window.image_y = 0
            self.main_window.image_scale = 1
            self.display_current_patch()

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

        elif self.current_mode == Mode.ZOOM:
            self.display_current_patch()
            return True

        else:
            return False

    def handle_motion(self, position):
        """
        Handle motion events of the mouse at the given position

        :param position: The position (x, y) of the mouse during the event
        :returns: True on success, False otherwise
        """

        if self.current_mode is not Mode.ZOOM:

            position = (position[0] - self.main_window.image_x,
                        position[1] - self.main_window.image_y)

            position = (position[0] / self.main_window.image_scale,
                        position[1] / self.main_window.image_scale)

        if self.current_mode == Mode.ADD_REGION:
            self.logger.debug("Adding region")

            draw_radius = self.add_region_radius / self.main_window.image_scale

            patch = self.image.patches[self.current_patch]
            patch.add_region(position, draw_radius)

            self.display_current_patch()

        elif self.current_mode == Mode.REMOVE_REGION:
            self.logger.debug("Removing Region")

            draw_radius = (self.remove_region_radius /
                           self.main_window.image_scale)

            patch = self.image.patches[self.current_patch]
            patch.remove_region(position, draw_radius)
            self.display_current_patch()

        elif self.current_mode == Mode.REMOVE_LANDMARK:
            draw_radius = (self.remove_landmark_radius /
                           self.main_window.image_scale)

            patch = self.image.patches[self.current_patch]
            patch.remove_landmark(position, draw_radius)
            self.display_current_patch()

        elif self.current_mode == Mode.ZOOM:
            self.main_window.image_x += (position[0] -
                                         self.main_window.previous_position[0])

            self.main_window.image_y += (position[1] -
                                         self.main_window.previous_position[1])

            self.display_current_patch()

        else:
            return False

        return True

    def adjust_threshold(self, wheel_rotation):
        """
        Adjust the current threshold of the patch mask

        :param wheel_rotation: The rotation of the mouse wheel
        :returns: None
        """

        patch = self.image.patches[self.current_patch]

        # Adjust the threshold.  Note that it is inverted, because it feels
        # more natural to scroll down to 'reduce' the region, rather than
        # reducing the threshold
        if wheel_rotation > 0 and patch.thresh > 0:
            patch.thresh -= 0.01

        elif wheel_rotation < 0 and patch.thresh < 1:

            patch.thresh += 0.01

        patch.apply_threshold(patch.thresh)
        patch.overlay_mask()

        self.logger.debug("Threshold value: {}".format(patch.thresh))
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

        self.main_window.set_brush_radius(self.remove_region_radius)
        self.main_window.draw_brush()
