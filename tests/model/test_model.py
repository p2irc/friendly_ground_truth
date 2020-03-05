"""
File Name: test_model.py

Authors: Kyle Seidenthal

Date: 04-03-2020

Description: Unit Testing for Model

"""

import pytest
import os
import numpy as np

from skimage import io
from friendly_ground_truth.model.model import Image, Patch


class TestImage:
    """
    Tests pertaining to the Image class
    """

    @pytest.fixture
    def valid_rgb_image_path(self):
        return os.path.abspath('tests/data/KyleS22.jpg')

    @pytest.fixture
    def valid_grayscale_image_path(self):
        return os.path.abspath('tests/data/KyleS22_gray.png')

    @pytest.fixture
    def invalid_image_path(self):
        return 'invalid/image/path'

    @pytest.fixture
    def test_image_data(self):
        return io.imread(os.path.abspath('tests/data/KyleS22.jpg'))

    def test_load_image_valid_rgb(self, valid_rgb_image_path):
        """
        Load a valid RGB image.

        :test_condition: This should load with no errors.

        :param valid_rgb_image_path: A path to a valid RGB image to load
        :returns: None
        """

        image = Image(valid_rgb_image_path)

        # Make sure there is an image
        assert image.image is not None

        # Make sure there are 100 patches
        assert len(image.patches) == 100

        # Make sure it has only one channel
        assert len(image.image.shape) == 2

        # Make sure it is a float64 image
        assert image.image.dtype == 'float64'

    def test_load_image_valid_grayscale(self, valid_grayscale_image_path):
        """
        Load a valid Grayscale image

        :test_condition: This should load with no errors.
        :param valid_grayscale_image_path: A path to a valid grayscale image
        :returns: None
        """
        image = Image(valid_grayscale_image_path)

        # Make sure there is an image
        assert image.image is not None

        # Make sure there are 100 patches
        assert len(image.patches) == 100

        # Make sure it has only one channel
        assert len(image.image.shape) == 2

        # Make sure it is a float64 image
        assert image.image.dtype == 'float64'

    def test_load_image_invalid_path(self, invalid_image_path):
        """
        Load an image from a non-existant path

        :test_condition: Should throw FileNotFoundException

        :param invalid_image_path: A non-existant path
        :returns: None
        """

        with pytest.raises(FileNotFoundError):
            image = Image(invalid_image_path)

    def test_create_patches_NONE_image(self, valid_rgb_image_path):
        """
        Try to create patches from a non-image datatype

        :test_condition: This should throw an exception.

        :returns: None
        """
        image_data = None
        image = Image(valid_rgb_image_path)

        with pytest.raises(ValueError):
            image.create_patches(image_data)

    def test_create_patches_X_divisible_by_num_patches(self, test_image_data):
        """
        Try to create patches from an image whose X size is evenly divisible
        by the number of patches (ie no padding is needed).

        :test_condition: The patches property should have image.num_patches**2
                         patches in its list, each with the correct size.

        :param test_image_data: A numpy array representing an image.
        :returns: None
        """

        assert False

    def test_create_patches_X_not_divisible_by_num_patches(self,
                                                           test_image_data):
        """
        Try to create patches from an image whose X size is not evenly
        divisible by the number of patches (ie padding is needed).

        :test_condition: The patches property should have image.num_patches**2
                         patches in its list, each with the correct size.

        :param test_image_data: A numpy array representing the image
        :returns: None
        """

        assert False

    def test_create_patches_Y_divisible_by_num_patches(self, test_image_data):
        """
        Try to create patches from an image whose Y size is evenly divisible by
        the number of patches (ie no padding is needed).

        :test_condition: The patches property should have image.num_patches**2
                         patches in its list, each with the correct size.

        :param test_image_data: A numpy array representing the image
        :returns: None
        """

        assert False

    def test_create_patches_Y_not_divisible_by_num_patches(self,
                                                           test_image_data):
        """
        Try to create patches from an image whose Y size is not evenly
        divisible by the number of patches (ie padding is needed)

        :test_condition: The patches property should have image.num_patches**2
                         patches in its list, each with the correct size.

        :param test_image_data: A numpy array representing the image
        :returns: None
        """

        assert False

    def test_create_mask_no_patches(self):
        """
        Create a mask when no patches have been created.  The mask should be
        an empty array.

        :test_condition: The mask should be an empty array

        :returns: None
        """

        assert False

    def test_create_mask(self):
        """
        Create a mask from a valid image

        :test_condition: The mask should be the same size as the original
                         image.

        :returns: None
        """

        assert False

    def test_export_mask(self):
        """
        Try to export the mask

        :test_condition: The image file should exist on the system.

        :returns: None
        """

        assert False
