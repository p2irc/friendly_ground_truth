"""
File Name: test_model.py

Authors: Kyle Seidenthal

Date: 04-03-2020

Description: Unit Testing for Model

"""

import pytest
from friendly_ground_truth.model.model import Image, Patch


class TestImage:
    """
    Tests pertaining to the Image class
    """

    @pytest.fixture
    def valid_rgb_image_path(self):
        # TODO
        return '/path/to/image'

    @pytest.fixture
    def valid_grayscale_image_path(self):
        # TODO
        return 'path/to/image'

    @pytest.fixture
    def invalid_image_path(self):
        return 'invalid/image/path'

    @pytest.fixture
    def test_image_data(self):
        # TODO: Load a test image into a numpy array
        return None

    def test_load_image_valid_rgb(self, valid_rgb_image_path):
        """
        Load a valid RGB image.

        :test_condition: This should load with no errors.

        :param valid_rgb_image_path: A path to a valid RGB image to load
        :returns: None
        """

        # TODO: load_image(valid_rgb_image_path)
        assert False

    def test_load_image_valid_grayscale(self, valid_grayscale_image_path):
        """
        Load a valid Grayscale image

        :test_condition: This should load with no errors.
        :param valid_grayscale_image_path: A path to a valid grayscale image
        :returns: None
        """

        assert False

    def test_load_image_invalid_path(self, invalid_image_path):
        """
        Load an image from a non-existant path

        :test_condition: This should throw an exception.

        :param invalid_image_path: A non-existant path
        :returns: None
        """

        assert False

    def test_create_patches_NONE_image(self):
        """
        Try to create patches from a non-image datatype

        :test_condition: This should throw an exception.

        :returns: None
        """
        image_data = None
        # TODO
        assert False

    def test_create_patches_X_divisible_by_num_patches(self, test_image_data):
        """
        Try to create patches from an image whose X size is evenly divisible
        by the number of patches (ie no padding is needed).

        :param test_image_data: A numpy array representing an image.
        :returns: None
        """

        assert False

    def test_create_patches_X_not_divisible_by_num_patches(self,
                                                           test_image_data):
        """
        Try to create patches from an image whose X size is not evenly
        divisible by the number of patches (ie padding is needed).

        :param test_image_data: A numpy array representing the image
        :returns: None
        """

        assert False

    def test_create_patches_Y_divisible_by_num_patches(self, test_image_data):
        """
        Try to create patches from an image whose Y size is evenly divisible by
        the number of patches (ie no padding is needed).

        :param test_image_data: A numpy array representing the image
        :returns: None
        """

        assert False

    def test_create_patches_Y_not_divisible_by_num_patches(self,
                                                           test_image_data):
        """
        Try to create patches from an image whose Y size is not evenly
        divisible by the number of patches (ie padding is needed)

        :param test_image_data: A numpy array representing the image
        :returns: None
        """

        assert False
