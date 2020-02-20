"""
File Name: model.py

Authors: Kyle Seidenthal

Date: 20-02-2020

Description: Contains the model elements for the application

"""
import logging
import numpy as np

from skimage import io
from skimage.util.shape import view_as_blocks

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

    def load_image(self, path):
        """
        Loads an image into a numpy array

        :param path: The path to the image to load
        :returns: An image in the form of a numpy array
        """

        self.logger.debug("Loading image")
        try:
            img = io.imread(path)
        except exception as e:
            logger.error("That image had some issues.")

        return img

    def create_patches(self, image, num_patches):
        """
        Create a list of patches from the image

        :param image: The image to create patches from
        :param num_patches: The number of patches to create ALONG ONE DIMENSION
        :returns: A list of patches made from the image
        """
        self.logger.debug("Creating patches")

        # Determine padding so we can use non-overlapping patches
        pad_x = (0, 0)
        pad_y = (0, 0)

        self.logger.debug(image.shape)

        if image.shape[0] % num_patches is not 0:
            pad_x = (0, (num_patches - (image.shape[0] % num_patches)))

        if image.shape[1] % num_patches is not 0:
            pad_y = (0, (num_patches - (image.shape[1] % num_patches)))

        self.logger.debug("{}, {}".format(pad_x, pad_y))

        image = np.pad(image, (pad_x, pad_y, (0, 0)), 'constant',
                       constant_values=(0, 0))

        # Get the size of each block
        block_size = (image.shape[0]//num_patches,
                      image.shape[1]//num_patches,
                      image.shape[2])

        self.logger.debug(image.shape)
        self.logger.debug(block_size)

        # Make the blocks
        blocks = view_as_blocks(image, block_shape=block_size)

        self.logger.debug(blocks.shape)

        patches = []

        # Create a list of new patch objects for viewing
        for i in range(num_patches):
            for j in range(num_patches):
                patch_data = blocks[i, j, 0]
                patches.append(Patch(patch_data, (i, j)))

        return patches


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
        self.logger = logging.getLogger('friendly_gt.model.Patch')
        self.patch = patch
        self.mask = np.zeros(self.patch.shape, dtype=bool)  # create empty mask
        self.patch_index = patch_index

        self.logger.debug("Created patch witth index {} and shape{}"
                          .format(patch_index, patch.shape))
