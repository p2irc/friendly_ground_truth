"""
File Name: test_image.py

Authors: Kyle Seidenthal

Date: 11-05-2020

Description: Tests for the Image class in the model

"""
import pytest
import os
import numpy as np

from skimage import io
from skimage.color import rgb2gray
from skimage import morphology
from skimage.draw import circle

from friendly_ground_truth.model.model import Image

from mock import MagicMock


class TestImage():
    """
    Base class for Image tests
    """

    @pytest.fixture
    def valid_rgb_image_path(self):
        return os.path.abspath('tests/data/KyleS22.jpg')

    @pytest.fixture
    def num_patches(self):
        return 10


class TestImageLoading(TestImage):
    """
    Test cases for the Image class loading the image
    """

    @pytest.fixture
    def valid_grayscale_image_path(self):
        return os.path.abspath('tests/data/KyleS22_gray.png')

    @pytest.fixture
    def invalid_image_path(self):
        return 'invalid/image/path'

    def test_load_image_valid_rgb(self, valid_rgb_image_path):
        """
        Test loading a valid RGB image

        Args:
            valid_rgb_image_path: A valid path to an RGB image

        Test Condition:
            The image property exists and is not None
            The length of the patches list is 100
            The resulting image has a single channel (Grayscale)
            The dtype of the image is float64
        """

        image = Image(valid_rgb_image_path)

        assert image.image is not None
        assert len(image.patches) == 100
        assert len(image.image.shape) == 2
        assert image.image.dtype == 'float64'

    def test_load_image_valid_grayscale(self, valid_grayscale_image_path):
        """
        Test loading a valid Grayscale image

        Args:
            valid_grayscale_image_path: A valid path to a Grayscale image

        Test Condition:
            The image property exists and is not None
            The length of the patches list is 100
            The resulting image has a single channel (Still Grayscale)
            The dtype of the image is float64
        """

        image = Image(valid_grayscale_image_path)

        assert image.image is not None
        assert len(image.patches) == 100
        assert len(image.image.shape) == 2
        assert image.image.dtype == 'float64'

    def test_load_image_invalid_path(self, invalid_image_path):
        """
        Test loading an image with an invalid path

        Args:
            invalid_image_path: An invalid path to an image.

        Test Condition:
            A FileNotFoundError is raised
        """
        with pytest.raises(FileNotFoundError):
            Image(invalid_image_path)


class TestImageCreatePatches(TestImage):
    @pytest.fixture
    def test_image_data(self):
        return rgb2gray(io.imread(os.path.abspath('tests/data/KyleS22.jpg')))

    @pytest.fixture
    def test_image_data_multi(self):
        return io.imread(os.path.abspath('tests/data/KyleS22.jpg'))

    @pytest.fixture
    def export_mask_path(self):
        return os.path.abspath('tests/data/test_mask.png')

    @pytest.fixture
    def export_label_path(self):
        return os.path.abspath('tests/data/test_labels.npy')

    @pytest.fixture(autouse=True)
    def remove_test_mask(self, export_mask_path, export_label_path):
        """
        Make sure the exported mask does not exist before or after any tests.

        :param export_mask_path: The path that the test mask will be created
                                 on
        :returns: None
        """

        backup_path = os.path.splitext(export_mask_path)[0]
        backup_path += "_bak.png"

        try:
            os.remove(export_mask_path)
        except FileNotFoundError:
            pass

        try:
            os.remove(export_label_path)
        except FileNotFoundError:
            pass

        try:
            os.remove(backup_path)
        except FileNotFoundError:
            pass

        yield

        try:
            os.remove(export_mask_path)
        except FileNotFoundError:
            pass

        try:
            os.remove(export_label_path)
        except FileNotFoundError:
            pass

        try:
            os.remove(backup_path)
        except FileNotFoundError:
            pass

    @pytest.fixture
    def patch_data_many_components(self):
        image_size = (500, 500)
        img = np.zeros(image_size, dtype=np.uint8)

        # This should make an image of non-neighbouring white pixels
        for i in range(image_size[0]):
            for j in range(image_size[1]):
                if i % 2 == 0 and i > 40:
                    if j % 2 == 0 and j > 40:
                        img[i, j] = 1
                    else:
                        pass

        rr, cc = circle(10, 10, 5)

        img[rr, cc] = 1

        return img
