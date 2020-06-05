"""
File Name: model.py

Authors: Kyle Seidenthal

Date: 11-05-2020

Description: Model Classes

"""
import logging
import numpy as np

from skimage import io, img_as_float, img_as_uint, img_as_ubyte
from skimage.util.shape import view_as_blocks
from skimage.filters import threshold_otsu
from skimage import color
from skimage.draw import circle


module_logger = logging.getLogger('friendly_gt.model')


class Image():
    """
    Represents a loaded image

    Attributes:
        path: The path to the image
        num_patches: The number of patches in a row
        image: The image array
        mask: The complete image mask
        patches: The list of Patches for this image
    """

    BG_LABEL = 0
    TIP_LABEL = 1
    BRANCH_LABEL = 2
    CROSS_LABEL = 3

    def __init__(self, path, num_patches=10, progress_update_func=None):
        """
        Initialize an image

        Args:
            path: The path to the image to load
            num_patches: The number of patches per row and column
                         (sqrt(total_patches))
            progress_update_func: A function used when updating a loading
                                  progress bar  The default value is None.

        Returns:
            An image object
        """
        self.logger = logging.getLogger('friendly_gt.model.Image')

        if num_patches <= 0:
            raise ValueError("num_patches must be a positive integer")

        self._path = path
        self._num_patches = num_patches
        self._progress_update_func = progress_update_func

        self._load_image()
        self._create_patches()

    @property
    def path(self):
        """
        Represents the path to the image file.


        Returns:
            The path to the image file.
        """
        return self._path

    @property
    def num_patches(self):
        """
        The number of patches to split each row into.


        Returns:
            The number of patches each row should be split into.
        """
        return self._num_patches

    @property
    def image(self):
        """
        The image data.


        Returns:
            The image data, a numpy array.
        """
        return self._image

    @property
    def mask(self):
        """
        The mask for the whole image.


        Returns:
            A boolean numpy array representing the image mask.
        """
        self._create_mask()
        return self._mask

    @property
    def patches(self):
        """
        A list of the patches for this image.


        Returns:
            A list of Patch objects.
        """
        return self._patches

    def _load_image(self):
        """
        Load the image associated with this instance

        Returns:
            None

        Postconditions:
            self._image and self_mask will be initialized
        """
        self.logger.debug("Loading image.")

        img = io.imread(self.path)
        img = color.rgb2gray(img)
        img = img_as_float(img)

        self._image = img
        self._mask = np.zeros(self._image.shape, dtype=bool)

    def _create_patches(self):
        """
        Create a list of patches from the image

        Returns:
            None

        Postconditions:
            self._patches will be set to a list of Patch objects
        """

        self.logger.debug("Creating patches.")

        # Determine padding so we can use non-overlapping patches
        pad_x = (0, 0)
        pad_y = (0, 0)

        if self.image.shape[0] % self.num_patches != 0:
            pad_x = (0, (self.num_patches - (self.image.shape[0] %
                     self.num_patches)))

        if self.image.shape[1] % self.num_patches != 0:
            pad_y = (0, (self.num_patches - (self.image.shape[1] %
                     self.num_patches)))
        image = np.pad(self.image, (pad_x, pad_y), 'constant',
                       constant_values=(0, 0))

        self._padded_shape = image.shape

        block_size = (image.shape[0]//self.num_patches,
                      image.shape[1]//self.num_patches)

        # Make the blocks
        blocks = view_as_blocks(image, block_shape=block_size)

        patches = []

        for i in range(self.num_patches):
            for j in range(self.num_patches):
                patch_data = blocks[i, j]
                patches.append(Patch(patch_data, (i, j)))

                if self._progress_update_func is not None:
                    self._progress_update_func()

        self._patches = patches

    def _create_mask(self):
        """
        Take the masks from all the patches and combine them into the mask for
        the whole image.


        Returns:
            None

        Postconditions:
            self._mask will be set to the combined mask
        """

        mask = np.zeros(self._padded_shape, dtype=bool)

        for patch in self.patches:
            r, c = patch.patch_index
            r = r * patch.patch.shape[0]
            c = c * patch.patch.shape[1]

            mask[r:r+patch.patch.shape[0],
                 c:c+patch.patch.shape[1]] += patch.mask

        self._mask = mask[:self.image.shape[0], :self.image.shape[1]]

    def create_overlay_img(self):
        """
        Create an overlay image using the mask.


        Returns:
            The image
        """

        shape = self._padded_shape[0], self._padded_shape[1], 3
        img = np.zeros(shape, dtype=self.patches[0].overlay_image.dtype)

        for patch in self.patches:
            r, c = patch.patch_index
            r = r * patch.patch.shape[0]
            c = c * patch.patch.shape[1]

            img[r:r+patch.patch.shape[0],
                c:c+patch.patch.shape[1], :] = patch.overlay_image

        return img[:self.image.shape[0], :self.image.shape[1], :]

    def _create_labelling(self):
        """
        Take the labellings from all patches and combine them into one matrix


        Returns:
            None

        Postconditions:
            self._landmark_matrix will be set
        """

        labels = np.zeros(self._padded_shape, dtype=np.uint8)

        for patch in self.patches:
            r, c = patch.patch_index
            r = r * patch.patch.shape[0]
            c = c * patch.patch.shape[1]

            labels[r:r+patch.patch.shape[0],
                   c:c+patch.patch.shape[1]] += patch.landmark_labels

        self._landmark_matrix = labels[:self.image.shape[0],
                                       :self.image.shape[1]]

    def export_mask(self, pathname):
        """
        Export the patch masks as a whole image mask

        Args:
            pathname: The path to the mask image file to save as.

        Returns:
            None

        Postconditions:
            A PNG image representing the mask will be saved at the
            specified path.
        """
        self._create_mask()

        # backup_path = os.path.splitext(pathname)[0]
        # backup_path += "_bak.png"
        # io.imsave(backup_path, img_as_uint(self.mask))

        # self._remove_small_components()
        io.imsave(pathname, img_as_uint(self.mask))

    def export_labels(self, pathname):
        """
        Export the labelling matrix

        Args:
            pathname: The path to the labelling matrix file

        Returns:
            None

        Postconditions:
            a .npy file will be saved at the specified path
        """

        self._create_labelling()
        np.save(pathname, self._landmark_matrix)

    def _remove_small_components(self):
        """
        Remove components that are not connected to the main root.


        Returns:
            None

        Postconditions:
            self._mask will be updated with the cleaned mask
        """
        from skimage.measure import label

        labels = label(self._mask)
        largestCC = labels == np.argmax(np.bincount(labels.flat)[1:])+1
        self._mask = largestCC


class Patch():
    """
    Represents an image patch

    Attributes:
        threshold: The current threshold for the mask
        patch: The patch image data
        mask: The mask for the patch
        patch_index: The index of this patch in the original image
        overlay_image: The patch image with the mask overlaid on top
        undo_history: The undo history for this patch
    """

    def __init__(self, patch, patch_index):
        """
        Create a patch object

        Args:
            patch: The image data for the patch
            patch_index: The index in the larger image of this patch

        Returns:
            A Patch object
        """

        self._logger = logging.getLogger('friendly_gt.model.Patch')

        self._patch = patch
        self._mask = np.zeros(self._patch.shape, dtype=bool)
        self._landmark_labels = np.zeros(self._patch.shape, dtype=np.uint8)

        self._patch_index = patch_index

        self._threshold = 1

        try:
            self.threshold = threshold_otsu(self._patch)
        except ValueError:
            self.threshold = 1

        self._overlay_image = None
        self._overlay_mask()

        self._old_flood_add_tolerance = 100
        self._old_flood_add_position = None

        self._old_flood_remove_tolerance = 100
        self._old_flood_remove_position = None

        self._undo_history = None

    @property
    def threshold(self):
        """
        The current threshold value for the patch.


        Returns:
            The value of the current threshold.
        """
        return self._threshold

    @threshold.setter
    def threshold(self, value):
        """
        Set the threshold for this patch.

        Args:
            value: The value to set the threshold to.

        Returns:
            None

        Postconditions:
            The threshold will be applied to the mask.
            The overlay_image property will be updated to show the new mask.
        """

        if value >= 0 and value <= 1:

            self._threshold = value
            self._apply_threshold(value)
            self._overlay_mask()

    @property
    def patch(self):
        """
        The patch data for this patch.


        Returns:
            A numpy array representing the image data for this patch.
        """
        return self._patch

    @property
    def mask(self):
        """
        The current mask for this patch.


        Returns:
            A numpy array representing the mask for this patch.
        """
        return self._mask

    @mask.setter
    def mask(self, mask):
        """
        Set the mask.

        Args:
            mask: The new mask, a boolean numpy array.

        Returns:
            None
        """
        self._mask = mask

    @property
    def landmark_labels(self):
        """
        The landmark label matrix for this patch.


        Returns:
            A numpy array containing class labellings for pixels in this patch.
        """
        return self._landmark_labels

    @property
    def patch_index(self):
        """
        The index of this patch in the larger parent image matrix.


        Returns:
            A tuple (i, j), the row and column index for this patch.
        """
        return self._patch_index

    @property
    def overlay_image(self):
        """
        The overlay image displaying the mask on top of the patch image data.


        Returns:
            A numpy array colour image.
        """
        return self._overlay_image

    @property
    def undo_history(self):
        return self._undo_history

    @undo_history.setter
    def undo_history(self, history):
        self._undo_history = history

    def _apply_threshold(self, value):
        """
        Apply a threshold to the patch mask

        Args:
            value: The value for the threshold

        Returns:
            None

        Postconditions:
            The _mask property will be updated with the new threshold
            applied

        Raises:
            ValueError if the value is not between 0 and 1
        """

        if value > 1 or value < 0:
            raise ValueError("Threshold values must be between 0 and 1")

        binary = self.patch > value
        self._mask = binary

    def _overlay_mask(self):
        """
        Overlay the current mask on the patch image


        Returns:
            None

        Postconditions:
            The _overlay_image property will contain the image with the
            binary mask over top.
        """

        labeling = np.copy(self._landmark_labels)
        labeling += self.mask

        c1 = 'red'
        c2 = 'green'
        c3 = 'orange'
        c4 = 'blue'

        colours = []
        unique_labels = np.unique(labeling)

        mapping = [(1, c1), (2, c2), (3, c3), (4, c4)]

        for m in mapping:
            if m[0] in unique_labels:
                colours.append(m[1])

        if len(colours) <= 0:
            colours = ['purple']

        colour_mask = color.label2rgb(labeling, image=self._patch,
                                      colors=colours, bg_label=0)

        self._overlay_image = img_as_ubyte(colour_mask)

    def clear_mask(self):
        """
        Clear the mask for this patch (set to all 0's)


        Returns:
            None

        Postconditions:
            The mask property will be reset to all 0's
        """
        self._mask = np.zeros(self.patch.shape, dtype=bool)
        self.threshold = 1

    def add_landmark(self, position, radius, label):
        """
        Label an area with the given label

        Args:
            position: The position to add the labelling (x, y)
            radius: The radius of a circle to label
            label: The class label for the pixels to be given

        Returns:
            None

        Postconditions:
            The _landmark_labels property will be udpated with the new
            landmark annotation.
        """
        rr, cc = self._get_circle(position, radius)

        self._landmark_labels[rr, cc] = label

        # Don't mark anything that isn't foreground
        self._landmark_labels[self.mask == 0] = 0
        self._overlay_mask()

    def remove_landmark(self, position, radius):
        """
        Un-label (label as 0) the pixels in the given region.


        Args:
            position: The position to un-label (x, y)
            radius: The radius of a circle to un-label

        Returns:
            None

        Postconditions:
            The _landmark_labels property will be updated with the new
            annotation.
        """

        rr, cc = self._get_circle(position, radius)

        self._landmark_labels[rr, cc] = 0

        self._overlay_mask()

    def add_region(self, position, radius):
        """
        Add a circular region to the mask at the given position.

        Args:
            position: The position to add the region (x, y)
            radius: The radius of the circular region

        Returns:
            None

        Postconditions:
            The _mask will be updated with the circular region set to 1's
        """

        position = round(position[0]), round(position[1])

        self._logger.debug("Add Position: {}".format(position))
        rr, cc = self._get_circle(position, radius)

        self._mask[rr, cc] = 1

        self._overlay_mask()

    def remove_region(self, position, radius):
        """
        Remove a circular region from the mask at the given position.

        Args:
            position: The position to remove the region at (x, y)
            radius: The radius of the circular region

        Returns:
            None

        Postconditions:
            The _mask will be updated with the circular region set to 0's
        """
        rr, cc = self._get_circle(position, radius)

        self._mask[rr, cc] = 0

        self._overlay_mask()

    def flood_add_region(self, position, tolerance):
        """
        Add to the current mask a flood region at the given position with the
        given tolerance.


        Args:
            position: The position to start the flood fill (x, y)
            tolerance: The tolerance for pixels to be included

        Returns:
            None

        Postconditions:
            The _mask will be updated with the new region.
        """

        from skimage.segmentation import flood

        position = int(position[0]), int(position[1])

        # If we are still editing the tolerance, we need to go back to the old
        # mask.
        if position == self._old_flood_add_position:
            self.mask = np.copy(self._old_mask)
        else:
            self._old_mask = np.copy(self._mask)

        add_mask = flood(self._patch, position, tolerance=tolerance)

        self._mask += add_mask

        self._overlay_mask()

        self._old_flood_add_tolerance = tolerance
        self._old_flood_add_position = position

    def flood_remove_region(self, position, tolerance):
        """
        Remove from the current mask a flood region at the given position with
        the given tolerance.

        Args:
            position: The position to start the flood fill (x, y)
            tolerance: The tolerance for pixels to be included

        Returns:
            None

        Postconditions:
            The _mask will be updated with the new region
        """
        from skimage.segmentation import flood

        position = int(position[0]), int(position[1])

        # If we are still editing the tolerance, we need to go back to the old
        # mask.
        if position == self._old_flood_remove_position:
            self.mask = np.copy(self._old_mask)
        else:
            self._old_mask = np.copy(self._mask)

        remove_mask = flood(self._patch, position, tolerance=tolerance)

        self._mask[remove_mask] = 0

        self._overlay_mask()

        self._old_flood_remove_tolerance = tolerance
        self._old_flood_remove_position = position

    def _get_circle(self, position, radius):
        """
        Return the indices of a circular region at the given position with the
        given radius.

        Args:
            position: (x, y) coordinates of the circle
            radius: The radius of the circle

        Returns:
            Two lists, rr and cc that represnt points in the circle
        """

        rr, cc = circle(position[0], position[1], radius)

        zipped = zip(rr, cc)

        fixed_pairs = []

        for pair in zipped:
            if (pair[0] >= 0 and pair[1] >= 0 and pair[0] < self._mask.shape[0]
                    and pair[1] < self.mask.shape[1]):
                fixed_pairs.append(pair)

        rr = []
        cc = []

        for p in fixed_pairs:
            rr.append(p[0])
            cc.append(p[1])

        return rr, cc
