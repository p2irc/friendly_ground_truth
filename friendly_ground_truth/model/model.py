"""
File Name: model.py

Authors: Kyle Seidenthal

Date: 20-02-2020

Description: Contains the model elements for the application

"""
import logging
import numpy as np

from skimage import io, img_as_float, img_as_ubyte, img_as_uint
from skimage.util.shape import view_as_blocks
from skimage.filters import threshold_otsu
from skimage import color
from skimage.draw import circle


module_logger = logging.getLogger('friendly_gt.model')


class Image():
    """
    Represents a loaded image
    """

    def __init__(self, path):
        """
        Initialize an image object

        :param path: The path to the image to load
        :returns: None
        """
        self.logger = logging.getLogger('friendly_gt.model.Image')

        self.path = path
        self.num_patches = 10
        self.image = self.load_image(path)
        self.mask = np.zeros(self.image.shape, dtype=bool)  # create empty mask
        self.patches = self.create_patches(self.image, self.num_patches)
        self.create_mask()

    def load_image(self, path):
        """
        Loads an image into a numpy array

        :param path: The path to the image to load
        :returns: An image in the form of a numpy array
        :raises: FileNotFoundError if the image does not exist
        """

        self.logger.debug("Loading image")
        img = io.imread(path)
        img = color.rgb2gray(img)
        img = img_as_float(img)

        return img

    def create_patches(self, image, num_patches):
        """
        Create a list of patches from the image

        :param image: The image to create patches from
        :param num_patches: The number of patches to create ALONG ONE DIMENSION
        :returns: A list of patches made from the image
        :raises: ValueError if the image is not a  single channel image
        """

        if num_patches <= 0:
            raise ValueError("num_patches must be a positive non-zero"
                             " integer.")

        if type(image) is not np.ndarray:
            raise ValueError("image must be of type np.ndarray")

        if len(image.shape) != 2:
            raise ValueError("image must be a single channel image")

        self.logger.debug("Creating patches")

        # Determine padding so we can use non-overlapping patches
        pad_x = (0, 0)
        pad_y = (0, 0)

        self.logger.debug(image.shape)

        if image.shape[0] % num_patches != 0:
            pad_x = (0, (num_patches - (image.shape[0] % num_patches)))

        if image.shape[1] % num_patches != 0:
            pad_y = (0, (num_patches - (image.shape[1] % num_patches)))

        print(image.shape, pad_x, pad_y)
        image = np.pad(image, (pad_x, pad_y), 'constant',
                       constant_values=(0, 0))

        print(image.shape)
        self.padded_shape = image.shape
        # Get the size of each block
        block_size = (image.shape[0]//num_patches,
                      image.shape[1]//num_patches)

        self.logger.debug(image.shape)
        self.logger.debug(block_size)

        # Make the blocks
        blocks = view_as_blocks(image, block_shape=block_size)

        self.logger.debug(blocks.shape)

        patches = []

        # Create a list of new patch objects for viewing
        for i in range(num_patches):
            for j in range(num_patches):
                patch_data = blocks[i, j]
                patches.append(Patch(patch_data, (i, j)))

        return patches

    def create_mask(self):
        """
        Take the masks from all the patches and combine them into the mask
        for the whole image

        :returns: None
        """

        mask = np.zeros(self.padded_shape, dtype=bool)

        col_num = 0
        row_num = 0

        for patch in self.patches:

            r, c = patch.patch_index
            r = r * patch.patch.shape[0]
            c = c * patch.patch.shape[1]
            mask[r:r+patch.patch.shape[0],
                 c:c+patch.patch.shape[1]] += patch.mask

            col_num += 1

            if col_num == self.num_patches:
                col_num = 0
                row_num += 1

        self.mask = mask[:self.image.shape[0], :self.image.shape[1]]

    def export_mask(self, pathname):
        """
        Export the patch masks as a whole image mask

        :param pathname: The path to the mask image file
        :returns: None
        """
        self.create_mask()
        print(pathname)
        self.remove_small_components()
        io.imsave(pathname, img_as_uint(self.mask))

    def remove_small_components(self):
        """
        Remove components that are not connected to the main root

        :returns: None
        """
        from skimage.measure import label

        labels = label(self.mask)
        largestCC = labels == np.argmax(np.bincount(labels.flat)[1:])+1
        self.mask = largestCC


class Patch():
    """
    Represents an image patch
    """

    def __init__(self, patch, patch_index):
        """
        Create a patch object

        :param patch: The image patch to use
        :returns: None
        """

        # The max number of components to consider before determining that
        # this patch has no roots in it
        self.MAX_COMPONENTS = 500

        # Whether or not to display this patch to the user
        self.display = True

        self.logger = logging.getLogger('friendly_gt.model.Patch')
        self.patch = patch
        self.mask = np.zeros(self.patch.shape, dtype=bool)  # create empty mask
        self.patch_index = patch_index

        self.thresh = threshold_otsu(self.patch)

        self.apply_threshold(self.thresh)

        self.check_displayable()

        self.overlay_image = None
        self.overlay_mask()

        self.logger.debug("Created patch with index {} and shape {}"
                          .format(patch_index, patch.shape))

        self.old_flood_add_tolerance = 100
        self.old_flood_add_position = None

    def apply_threshold(self, value):
        """
        Apply a threshold to the patch mask

        :param value: The pixel value (floating point) to use as a threshold
        :returns: None
        :postcondition: The patch mask will be updated with the new threshold
        :raises: ValueError if the value is not between 0 and 1
        """

        if value > 1 or value < 0:
            raise ValueError("Threshold values must be between 0 and 1")

        binary = self.patch > value
        self.mask = binary

    def overlay_mask(self):
        """
        Overlay the current patch mask on the patch image

        :returns: None
        :postcondition: The overlay property will contain the image with the
                        binary mask on top.
        """

        alpha = 0.6

        color_mask = np.zeros((self.patch.shape[0], self.patch.shape[1], 3),
                              dtype=np.float64)

        color_mask[:, :, 0] = self.mask

        img_color = np.dstack((self.patch, self.patch, self.patch))
        img_hsv = color.rgb2hsv(img_color)
        color_mask_hsv = color.rgb2hsv(color_mask)

        img_hsv[:, :, 0] = color_mask_hsv[:, :, 0]
        img_hsv[:, :, 1] = color_mask_hsv[:, :, 1] * alpha

        img_masked = color.hsv2rgb(img_hsv)
        img_masked = img_as_ubyte(img_masked)

        self.overlay_image = img_masked

    def clear_mask(self):
        """
        Set the mask for this patch to be empty (all 0's)

        :returns: None
        :postcondition: The mask property will contain all 0's
        """

        self.mask = np.zeros(self.patch.shape, dtype=bool)
        self.thresh = 1

    def add_region(self, position, radius):
        """
        Add a circular region to the mask at the given position

        :param position: The position in the mask to add the region
        :param radius: The radius of the region to add
        :returns: None
        :postcondition: The circular region in the mask will be set to 1's
        """
        self.logger.debug("Add Region Position {}".format(position))
        rr, cc = circle(position[1], position[0], radius)
        self.mask[rr, cc] = 1
        self.overlay_mask()

    def remove_region(self, position, radius):
        """
        Remove a circular region from the mask at the given position

        :param position: The position in the mask to remove the region
        :param radius: The radius of the region to remove
        :returns: None
        :postcondition: The region in the mask will be set to 0's
        """

        rr, cc = circle(position[1], position[0], radius)
        self.mask[rr, cc] = 0
        self.overlay_mask()

    def flood_add_region(self, position, tolerance):
        """
        Add to the current mask a flood region at the given position with the
        given tolerance

        :param position: The position to start the flood fill
        :param tolerance: The tolerance for pixels to be included
        :returns: None
        """
        self.logger.debug("Flood Position: {}".format(position))
        self.logger.debug("Flood Tolerance: {}".format(tolerance))

        self.logger.debug("Mask Shape {}".format(self.mask.shape))
        self.logger.debug("Patch Shape {}".format(self.patch.shape))

        from skimage.segmentation import flood

        position = int(position[1]), int(position[0])

        # If we are still editing the tolerance, we need to go back to the old
        # mask
        if position == self.old_flood_add_position:
            self.logger.debug("Reverting mask ")
            self.mask = np.copy(self.old_mask)
            self.overlay_mask()
        else:
            self.logger.debug("Storing old mask")
            self.old_mask = np.copy(self.mask)

        add_mask = flood(self.patch, position, tolerance=tolerance)

        self.mask += add_mask

        self.old_flood_add_tolerance = tolerance
        self.old_flood_add_position = position

    def flood_remove_region(self, position, tolerance):
        """
        Remove from the current mask a flood region at the given position with
        the given tolerance

        :param position: The position to start the flood fill
        :param tolerance: The tolerance for pixels to be included
        :returns: None
        """

        from skimage.segmentation import flood

        position = int(position[1]), int(position[0])

        # If we are still editing the tolerance, we need to go back to the old
        # mask
        if position == self.old_flood_remove_position:
            self.logger.debug("Reverting mask ")
            self.mask = np.copy(self.old_mask)
            self.overlay_mask()
        else:
            self.logger.debug("Storing old mask")
            self.old_mask = np.copy(self.mask)

        remove_mask = flood(self.patch, position, tolerance=tolerance)

        self.mask[remove_mask] = 0

        self.old_flood_add_tolerance = tolerance
        self.old_flood_add_position = position

    def check_displayable(self):
        """
        Set patches as non-displayable if they are not likely to contain roots

        :returns: None
        """
        from skimage import morphology

        # Use the number of connected components in the patch to determine
        # if it probably does not contain roots
        unique = np.unique(morphology.label(self.mask))
        num_components = len(unique) - 2

        if num_components > self.MAX_COMPONENTS:
            self.clear_mask()
            self.display = False
