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
from skimage.color import rgb2gray
from skimage import morphology
from skimage.draw import circle

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
        return rgb2gray(io.imread(os.path.abspath('tests/data/KyleS22.jpg')))

    @pytest.fixture
    def test_image_data_multi(self):
        return io.imread(os.path.abspath('tests/data/KyleS22.jpg'))

    @pytest.fixture
    def num_patches(self):
        return 10

    @pytest.fixture
    def export_mask_path(self):
        return os.path.abspath('tests/data/test_mask.png')

    @pytest.fixture(autouse=True)
    def remove_test_mask(self, export_mask_path):
        """
        Make sure the exported mask does not exist before or after any tests.

        :param export_mask_path: The path that the test mask will be created
                                 on
        :returns: None
        """
        try:
            os.remove(export_mask_path)
        except FileNotFoundError:
            pass

        yield

        try:
            os.remove(export_mask_path)
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
            Image(invalid_image_path)

    def test_create_patches_NONE_image(self, valid_rgb_image_path,
                                       num_patches):
        """
        Try to create patches from a non-image datatype

        :test_condition: This should throw an exception.

        :returns: None
        """
        image_data = None
        image = Image(valid_rgb_image_path)

        with pytest.raises(ValueError):
            image.create_patches(image_data, num_patches)

    def test_create_patches_multi_channel_image(self, num_patches,
                                                valid_rgb_image_path,
                                                test_image_data_multi):
        """
        Try to create patches of a multi channel image

        :test_condition: A ValueError should be raised

        :param num_patches: The number of patches to use
        :param test_image_data: Multi channel image data
        :returns: None
        """

        image = Image(valid_rgb_image_path)

        with pytest.raises(ValueError):
            image.create_patches(test_image_data_multi, num_patches)

    def test_create_patches_X_divisible_by_num_patches(
                                                      self,
                                                      valid_rgb_image_path,
                                                      test_image_data):
        """
        Try to create patches from an image whose X size is evenly divisible
        by the number of patches (ie no padding is needed).

        :test_condition: The patches property should have image.num_patches**2
                         patches in its list, each with the correct size.

        :param test_image_data: A numpy array representing an image.
        :returns: None
        """

        image = Image(valid_rgb_image_path)
        NUM_PATCHES = 10
        image = Image(valid_rgb_image_path)

        # if the images X length is not divisible by the number of patches,
        # pad it

        if test_image_data.shape[1] % NUM_PATCHES != 0:
            pad_x = (0, (NUM_PATCHES -
                         (test_image_data.shape[0] % NUM_PATCHES)))
            pad_y = (0, 0)
            img = np.pad(test_image_data, (pad_x, pad_y), 'constant',
                         constant_values=(0, 0))
        else:
            img = test_image_data

        patches = image.create_patches(img, NUM_PATCHES)

        assert len(patches) == NUM_PATCHES**2

    def test_create_patches_X_not_divisible_by_num_patches(
                                                          self,
                                                          valid_rgb_image_path,
                                                          test_image_data):
        """
        Try to create patches from an image whose X size is not evenly
        divisible by the number of patches (ie padding is needed).

        :test_condition: The patches property should have image.num_patches**2
                         patches in its list, each with the correct size.

        :param test_image_data: A numpy array representing the image
        :returns: None
        """
        NUM_PATCHES = 10
        image = Image(valid_rgb_image_path)

        # if the images X length is divisible by the number of patches, pad it
        if test_image_data.shape[1] % NUM_PATCHES == 0:
            pad_x = (0, test_image_data.shape[1] + 1)
            pad_y = (0, 0)
            img = np.pad(test_image_data, (pad_x, pad_y), 'constant',
                         constant_values=(0, 0))
        else:
            img = test_image_data

        patches = image.create_patches(img, NUM_PATCHES)

        assert len(patches) == NUM_PATCHES**2

    def test_create_patches_Y_divisible_by_num_patches(self,
                                                       valid_rgb_image_path,
                                                       test_image_data):
        """
        Try to create patches from an image whose Y size is evenly divisible by
        the number of patches (ie no padding is needed).

        :test_condition: The patches property should have image.num_patches**2
                         patches in its list, each with the correct size.

        :param test_image_data: A numpy array representing the image
        :returns: None
        """
        NUM_PATCHES = 10
        image = Image(valid_rgb_image_path)

        # if the images Y length is not divisible by the number of patches,
        # pad it

        if test_image_data.shape[1] % NUM_PATCHES != 0:
            pad_y = (0, (NUM_PATCHES -
                         (test_image_data.shape[1] % NUM_PATCHES)))
            pad_x = (0, 0)
            img = np.pad(test_image_data, (pad_x, pad_y), 'constant',
                         constant_values=(0, 0))
        else:
            img = test_image_data

        patches = image.create_patches(img, NUM_PATCHES)

        assert len(patches) == NUM_PATCHES**2

    def test_create_patches_Y_not_divisible_by_num_patches(
                                                          self,
                                                          valid_rgb_image_path,
                                                          test_image_data):
        """
        Try to create patches from an image whose Y size is not evenly
        divisible by the number of patches (ie padding is needed)

        :test_condition: The patches property should have image.num_patches**2
                         patches in its list, each with the correct size.

        :param test_image_data: A numpy array representing the image
        :returns: None
        """
        NUM_PATCHES = 10
        image = Image(valid_rgb_image_path)

        # if the images Y length is divisible by the number of patches, pad it
        if test_image_data.shape[1] % NUM_PATCHES == 0:
            pad_y = (0, test_image_data.shape[1] + 1)
            pad_x = (0, 0)
            img = np.pad(test_image_data, (pad_x, pad_y), 'constant',
                         constant_values=(0, 0))
        else:
            img = test_image_data

        patches = image.create_patches(img, NUM_PATCHES)

        assert len(patches) == NUM_PATCHES**2

    def test_create_patches_invalid_num_patches(self, valid_rgb_image_path,
                                                test_image_data):
        """
        Test creating patches with an invalid (0 or negative) number of patches


        :test_condition: A value error should be raised

        :param test_image_data: The image data array
        :returns: None
        """
        image = Image(valid_rgb_image_path)

        with pytest.raises(ValueError):
            image.create_patches(test_image_data, -5)

        with pytest.raises(ValueError):
            image.create_patches(test_image_data, 0)

    def test_create_mask(self, valid_rgb_image_path):
        """
        Create a mask from a valid image

        :test_condition: The mask should be the same size as the original
                         image.

        :returns: None
        """
        image = Image(valid_rgb_image_path)

        image.create_mask()

        assert image.mask.shape == image.image.shape

    def test_export_mask(self, valid_rgb_image_path, export_mask_path):
        """
        Try to export the mask

        :test_condition: The image file should exist on the system.

        :returns: None
        """
        image = Image(valid_rgb_image_path)

        image.export_mask(export_mask_path)

        assert os.path.exists(export_mask_path)

    def test_remove_small_components(self, valid_rgb_image_path,
                                     patch_data_many_components):
        """
        Test removing small components

        :param valid_rgb_image_path: The valid rgb image path
        :returns: None
        """

        image = Image(valid_rgb_image_path)
        image.mask = patch_data_many_components

        image.remove_small_components()

        unique = np.unique(morphology.label(image.mask))

        num_components = len(unique)

        assert num_components == 2


class TestPatch:

    @pytest.fixture
    def patch_data_many_components(self):
        image_size = (500, 500)
        img = np.zeros(image_size, dtype=np.uint8)

        # This should make an image of non-neighbouring white pixels
        for i in range(image_size[0]):
            for j in range(image_size[1]):
                if i % 2 == 0:
                    if j % 2 == 0:
                        img[i, j] = 1
                    else:
                        pass
        return img

    @pytest.fixture
    def patch_data_two_components(self):
        image_size = (500, 500)
        img = np.zeros(image_size, dtype=np.uint8)
        img[0:image_size[0]/2, image_size[1]:image_size[1]/2] = 1

        return img

    @pytest.fixture
    def patch_data_ones(self):
        image_size = (500, 500)
        img = np.ones(image_size, dtype=np.uint8)

        return img

    @pytest.fixture
    def patch_data_zeros(self):
        image_size = (500, 500)
        img = np.zeros(image_size, dtype=np.uint8)

        return img

    @pytest.fixture
    def patch_index(self):
        return (1, 1)

    def test_apply_threshold_negative_value(self, patch_data_many_components,
                                            patch_index):
        """
        Try to apply a negative threshold value

        :test_condition: Should raise a ValueError

        :returns: None
        """
        patch = Patch(patch_data_many_components, patch_index)

        with pytest.raises(ValueError):
            patch.apply_threshold(-1)

    def test_apply_threshold_integer_value(self, patch_data_many_components,
                                           patch_index):
        """
        Try to apply a threshold greater than 1

        :test_condition: Should raise a ValueError

        :returns: None
        """

        patch = Patch(patch_data_many_components, patch_index)

        with pytest.raises(ValueError):
            patch.apply_threshold(2)

    def test_overlay_mask(self, patch_data_many_components, patch_index):
        """
        Make sure that overlaying the mask works correctly

        :test_condition: The overlay_mask property is an image with the same
                         shape as the original image

        :returns: None
        """

        patch = Patch(patch_data_many_components, patch_index)

        patch.overlay_mask()

        assert patch.overlay_image.shape[0:2] == patch.patch.shape

    def test_clear_mask(self, patch_data_many_components,
                        patch_data_ones, patch_index):
        """
        See what happens when we try to clear the mask

        :test_condition: The mask will be all zeros

        :returns: None
        """
        patch = Patch(patch_data_many_components, patch_index)

        patch.mask = patch_data_ones

        patch.clear_mask()

        assert np.count_nonzero(patch.mask) == 0

    def test_add_region(self, patch_data_zeros, patch_data_many_components,
                        patch_index):
        """
        Check that the given region is added

        :test_condition: The mask at the given position is 1


        :returns: None
        """
        position = (patch_data_zeros.shape[0]//2,
                    patch_data_zeros.shape[1]//2)

        radius = 10

        patch = Patch(patch_data_many_components, patch_index)
        patch.mask = patch_data_zeros

        patch.add_region(position, radius)

        assert patch.mask[position[0], position[1]] == 1

    def test_remove_region(self, patch_data_ones, patch_data_many_components,
                           patch_index):
        """
        Check that a given region is removed

        :test_condition: The mask at the given position is 0


        :returns: None
        """
        position = (patch_data_ones.shape[0]//2,
                    patch_data_ones.shape[1]//2)

        radius = 10

        patch = Patch(patch_data_many_components, patch_index)
        patch.mask = patch_data_ones

        patch.remove_region(position, radius)

        assert patch.mask[position[0], position[1]] == 0

    def test_check_displayable(self, patch_data_many_components, patch_index):
        """
        Check that a mask with more than MAX_COMPONENTS is set to not
        displayable

        :test_condition: A mask with > MAX_COMPINENTS has displayable == False

        :returns: None
        """
        patch = Patch(patch_data_many_components, patch_index)

        patch.mask = patch_data_many_components

        patch.check_displayable()

        assert patch.display is False

    def test_flood_add_region_new_pos(self, patch_data_zeros, patch_index,
                                      patch_data_many_components):
        """
        Test flood add region with a new input position

        test_condition: The mask at the given position is 1

        :returns: None
        """

        position = (patch_data_zeros.shape[0]//2,
                    patch_data_zeros.shape[1]//2)

        tolerance = 0.0001

        patch = Patch(patch_data_many_components, patch_index)
        patch.mask = patch_data_zeros
        patch.old_flood_add_position = (0, 0)

        patch.flood_add_region(position, tolerance)

        assert patch.mask[position[0], position[1]] == 1

    def test_flood_add_region_old_pos(self, patch_data_zeros, patch_index,
                                      patch_data_many_components):
        """
        Test flood add region with an old input position

        :test_condition: The mask at the given position is 1

        :param patch_data_zeros: A numpy array of zeros
        :param patch_index: The patch index
        :param patch_data_many_components: A numpy array with many connected
                                           components
        :returns: None
        """

        position = (patch_data_zeros.shape[0]//2,
                    patch_data_zeros.shape[1]//2)

        tolerance = 0.0001

        patch = Patch(patch_data_many_components, patch_index)
        patch.mask = patch_data_zeros
        patch.old_flood_add_position = position
        patch.old_mask = patch_data_zeros

        patch.flood_add_region(position, tolerance)

        assert patch.mask[position[0], position[1]] == 1

    def test_flood_remove_region_new_pos(self, patch_data_ones, patch_index,
                                         patch_data_many_components):
        """
        Test flood remove region with a new input position

        test_condition: The mask at the given position is 0

        :returns: None
        """

        position = (patch_data_ones.shape[0]//2,
                    patch_data_ones.shape[1]//2)

        tolerance = 0.0001

        patch = Patch(patch_data_many_components, patch_index)
        patch.mask = patch_data_ones
        patch.old_flood_remove_position = (0, 0)

        patch.flood_remove_region(position, tolerance)

        assert patch.mask[position[0], position[1]] == 0

    def test_flood_remove_region_old_pos(self, patch_data_ones, patch_index,
                                         patch_data_many_components):
        """
        Test flood remove region with an old input position

        :test_condition: The mask at the given position is 0

        :param patch_data_zeros: A numpy array of zeros
        :param patch_index: The patch index
        :param patch_data_many_components: A numpy array with many connected
                                           components
        :returns: None
        """

        position = (patch_data_ones.shape[0]//2,
                    patch_data_ones.shape[1]//2)

        tolerance = 0.0001

        patch = Patch(patch_data_many_components, patch_index)
        patch.mask = patch_data_ones
        patch.old_flood_remove_position = position
        patch.old_mask = patch_data_ones

        patch.flood_remove_region(position, tolerance)

        assert patch.mask[position[0], position[1]] == 0
