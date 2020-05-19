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
    def setup(self, mocker):
        mocker.patch("friendly_ground_truth.model.model.Patch")

    @pytest.fixture
    def valid_rgb_image_path(self):
        return os.path.abspath('tests/data/KyleS22.jpg')

    @pytest.fixture
    def num_patches(self):
        return 10

    @pytest.fixture
    def test_image_data(self):
        return rgb2gray(io.imread(os.path.abspath('tests/data/KyleS22.jpg')))

    @pytest.fixture
    def test_image_data_multi(self):
        return io.imread(os.path.abspath('tests/data/KyleS22.jpg'))


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

    def test_load_image_valid_rgb(self, setup, valid_rgb_image_path):
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

    def test_load_image_valid_grayscale(self, setup,
                                        valid_grayscale_image_path):
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

    def test_load_image_invalid_path(self, setup, invalid_image_path):
        """
        Test loading an image with an invalid path

        Args:
            invalid_image_path: An invalid path to an image.

        Test Condition:
            A FileNotFoundError is raised
        """
        with pytest.raises(FileNotFoundError):
            Image(invalid_image_path)

    def test_create_image_invalid_patches(self, setup, valid_rgb_image_path):
        """
        Test creating an Image object with a negative patch number

        Args:
            valid_rgb_image_path: A patch to a valid RGB image

        Test Condition:
            Raises ValueError
        """

        with pytest.raises(ValueError):
            Image(valid_rgb_image_path, num_patches=-1)

    def test_image_get_mask(self, setup, valid_rgb_image_path):
        """
        Test getting the image mask

        Args:
            valid_rgb_image_path: A valid path to an RGB image

        Test Condition:
            A numpy array is returned
        """

        image = Image(valid_rgb_image_path)

        assert type(image.mask) == np.ndarray


class TestImageCreatePatches(TestImage):
    """
    Tests for the image class related to creating the patches from a loaded
    image
    """
    def test_create_patches_progress(self, setup, valid_rgb_image_path,
                                     num_patches, test_image_data,
                                     mocker):
        """
        Test creating patches from an image when a progress function is given

        Args:
            valid_rgb_image_path: A valid path to an RGB image
            num_patches: The number of patches
            test_image_data: A numpy array representing an image
            mocker: The mocker interface

        Test Condition:
            The progress function is called
        """

        prog_func = MagicMock()

        image = Image(valid_rgb_image_path, num_patches=num_patches,
                      progress_update_func=prog_func)

        if test_image_data.shape[1] % num_patches != 0:
            pad_x = (0, (num_patches -
                     (test_image_data.shape[0] % num_patches)))

            pad_y = (0, (num_patches -
                     (test_image_data.shape[1] % num_patches)))

            img = np.pad(test_image_data, (pad_x, pad_y), 'constant',
                         constant_values=(0, 0))

        else:
            img = test_image_data

        image._image = img
        image._create_patches()

        prog_func.assert_called()


class TestImageExports(TestImage):
    """
    Tests for the image class related to exporting and creating the whole image
    mask
    """
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

    @pytest.fixture
    def mock_patches(self, mocker, valid_rgb_image_path):
        img = io.imread(valid_rgb_image_path)
        mock_patches = []

        patch_shape = (int(img.shape[0]/3), int(img.shape[1]/3))

        for i in range(3):
            for j in range(3):
                mock_patch = MagicMock()
                mock_patch.patch_index = (i, j)
                mock_patch.patch = img[i:i+patch_shape[0], j:j+patch_shape[1]]
                mock_patch.mask = np.ones(patch_shape, dtype=bool)
                mock_patch.landmark_labels = np.ones(patch_shape,
                                                     dtype=np.uint8)
                mock_patches.append(mock_patch)

        return mock_patches

    def test_create_mask(self, setup, valid_rgb_image_path, mock_patches):
        """
        Test creating a mask from the patches in the image.

        Args:
            valid_rgb_image_path: A path to a valid RGB image

        Test Condition:
            The shapes of the images mask is the same as the images shape
            The type of the mask is boolean
        """

        image = Image(valid_rgb_image_path)

        image._patches = mock_patches

        image._create_mask()

        assert image.mask.shape == image.image.shape
        assert image.mask.dtype == bool

    def test_create_labelling(self, setup, valid_rgb_image_path, mock_patches):
        """
        Test creating a labelling matrix from image labels.

        Args:
            valid_rgb_image_path: A path to a valid RGB image.

        Test Condition:
            The shape of the image mask is the same as the image shape
        """
        image = Image(valid_rgb_image_path)

        image._patches = mock_patches

        image._create_labelling()

        assert image._landmark_matrix.shape == image.image.shape

    def test_export_mask(self, setup, valid_rgb_image_path, export_mask_path,
                         mock_patches):
        """
        Test exporting the mask to a PNG file.

        Args:
            valid_rbg_image_path: A path to a valid RGB image.
            export_mask_path: The path to save the exported mask to

        Test Condition:
            The PNG mask file should exist.
        """

        image = Image(valid_rgb_image_path)

        image._patches = mock_patches

        image.export_mask(export_mask_path)

        assert os.path.exists(export_mask_path)

    def test_export_labels(self, setup, valid_rgb_image_path,
                           export_label_path, mock_patches):
        """
        Test exporting a landmark label matrix.

        Args:
            setup: Setup for Image tests
            valid_rgb_image_path: A path to a valid RGB image.

        Test Condition:
            The label matrix exists on the file system.
        """

        image = Image(valid_rgb_image_path)

        image._patches = mock_patches

        image.export_labels(export_label_path)

        assert os.path.exists(export_label_path)

    def test_remove_small_components(self, setup, valid_rgb_image_path,
                                     patch_data_many_components):
        """
        Test removing small components from the mask.

        Args:
            setup: Setup for Image tests
            valid_rgb_image_path: A path to a valid RGB image

        Test Condition:
            The number of components in the mask is 2 (background and a single
            foreground)
        """

        image = Image(valid_rgb_image_path)

        image._mask = patch_data_many_components

        image._remove_small_components()

        unique = np.unique(morphology.label(image._mask))

        num_components = len(unique)

        assert num_components == 2
