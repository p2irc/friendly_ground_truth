"""
File Name: model.py

Authors: Kyle Seidenthal

Date: 20-02-2020

Description: Contains the model elements for the application

"""
import logging
import skimage

module_logger = logging.getLogger('friendly_gt.model')


class Image():
    """
    Represents a loaded image
    """

    def __init__(self, path, patch_size):
        """
        Initialize an image object

        :param path: The path to the image to load
        :param patch_size: The size of the patches that should be made from
                           the image
        :returns: None
        """
        self.logger = logging.getLogger('friendly_gt.model.Image')

        self.path = path
        self.patch_size = patch_size

        self.image = self.load_image(path)
        self.mask = None  # TODO: create empty mask
        self.patches = self.create_patches(self.image, self.patch_size)

    def load_image(self, path):
        """
        Loads an image into a numpy array

        :param path: The path to the image to load
        :returns: An image in the form of a numpy array
        """

        self.logger.debug("Loading image")
        pass

    def create_patches(self, image):
        """
        Create a list of patches from the image

        :param image: The image to create patches from
        :returns: A list of patches made from the image
        """
        self.logger.debug("Creating patches")
        pass


class Patch():
    """
    Represents an image patch
    """

    def __init__(self, patch):
        """
        Create a patch object

        :param patch: The image patch to use
        :returns: None
        """
        self.logger = logging.getlogger('friendly_gt.model.Patch')
        self.patch = patch
        self.mask = None  # TODO create empty mask
