"""
File Name: test_patch.py

Authors: Kyle Seidenthal

Date: 12-05-2020

Description: Tests for the Patch class.

"""

import pytest
import os
import numpy as np

from skimage import io
from skimage.color import rgb2gray

from friendly_ground_truth.model.model import Patch


class TestPatch():
    """
    Fixtures needed for testing Patches
    """

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

    @pytest.fixture
    def test_image_data(self):
        return rgb2gray(io.imread(os.path.abspath('tests/data/KyleS22.jpg')))


class TestAuxFuncs(TestPatch):
    """
    Tests for private functionality.

    """

    def test_threshold_valid(self, test_image_data):
        """
        Test setting the threshold with a value between 0 and 1


        Test Condition:
            self.threshold is set to the value
            The mask is changed
        """

        patch_data = test_image_data[:100, :100]

        patch = Patch(patch_data, (1, 1))

        old_mask = np.copy(patch.mask)

        patch.threshold = 0.7

        assert patch.threshold == 0.7
        np.testing.assert_equal(np.any(np.not_equal(old_mask, patch.mask)),
                                True)

    def test_threshold_invalid(self, test_image_data):
        """
        Test setting the threshold to a value above 1

        Args:
            test_image_data: Image data for testing

        Test Condition:
            The threshold does not change
            The mask is the same
        """
        patch_data = test_image_data[:100, :100]

        patch = Patch(patch_data, (1, 1))

        old_mask = np.copy(patch.mask)
        old_thresh = patch.threshold

        patch.threshold = 1.2

        assert patch.threshold == old_thresh
        np.testing.assert_equal(np.any(np.not_equal(old_mask, patch.mask)),
                                False)

    def test_init_all_black(self, patch_data_zeros):
        """
        Test making a patch where the image is all black and threshold_otsu
        fails.

        Args:
            patch_data_zeros: A numpy array of all zero image data

        Test Condition:
            The threshold is set to 1
        """

        patch = Patch(patch_data_zeros, (2, 3))

        assert patch.threshold == 1

    def test_set_mask(self, patch_data_zeros, patch_data_many_components):
        """
        Test setting the mask

        Args:
            patch_data_zeros: Image data with all zeros

        Test Condition:
            The mask property is set to the given mask
        """

        patch = Patch(patch_data_zeros, (5, 6))

        patch.mask = patch_data_many_components

        np.testing.assert_equal(np.any(np.equal(patch_data_many_components,
                                patch.mask)),
                                True)

    def test_get_patch_index(self, patch_data_zeros):
        """
        Test getting the patch index

        Args:
            patch_data_zeros: Image data with all zeros

        Test Condition:
            The correct patch index is returned
        """

        patch = Patch(patch_data_zeros, (4, 5))

        assert patch.patch_index == (4, 5)

    def test_overlay_mask(self, test_image_data, patch_data_ones):
        """
        Test overlaying the mask on the image.

        Args:
            test_image_data: Image data for testing
            patch_data_ones: Image data all ones.

        Test Condition:
            overlay_image is a numpy array with the same shape as the
                patch
        """

        img = test_image_data[:patch_data_ones.shape[0],
                              :patch_data_ones.shape[1]]

        patch = Patch(img, (2, 3))

        patch.mask = patch_data_ones

        patch._overlay_mask()

        assert patch.overlay_image.shape[:2] == patch.patch.shape

    def test_get_circle(self, patch_data_ones):
        """
        Test getting a circle.

        Args:
            patch_data_ones: Image data all ones

        Test Condition:
            Returns correct coordinate lists.
        """

        patch = Patch(patch_data_ones, (4, 3))

        position = (2, 2)
        radius = 2

        expected_rr = [1, 1, 1, 2, 2, 2, 3, 3, 3]
        expected_cc = [1, 2, 3, 1, 2, 3, 1, 2, 3]

        rr, cc = patch._get_circle(position, radius)

        assert rr == expected_rr
        assert cc == expected_cc

        position = (0, 0)
        radius = 2

        expected_rr = [0, 0, 1, 1]
        expected_cc = [0, 1, 0, 1]

        x, y = patch_data_ones.shape[0], patch_data_ones.shape[1]

        position = (x, y)
        radius = 2

        expected_rr = [x-1]
        expected_cc = [y-1]

        rr, cc = patch._get_circle(position, radius)

        assert rr == expected_rr
        assert cc == expected_cc


class TestAddToMask(TestPatch):
    """
    Tests for functions that add to the mask.

    """

    def test_apply_threshold(self, test_image_data):
        """
        Test applying a valid threshold

        Args:
            test_image_data: Image data for testing, a numpy array

        Test Condition:
            The mask is changed
        """

        patch_data = test_image_data[:130, :100]

        patch = Patch(patch_data, (1, 2))

        old_mask = np.copy(patch.mask)

        patch._apply_threshold(0.3)

        np.testing.assert_equal(np.any(np.not_equal(old_mask, patch.mask)),
                                True)

    def test_apply_threshold_invalid(self, test_image_data):
        """
        Test applying and invalid threshold.

        Args:
            test_image_data: Imag data for testing, a numpy array

        Test Condition:
            Raises ValueError
        """

        patch_data = test_image_data[:70, :130]

        patch = Patch(patch_data, (1, 4))

        with pytest.raises(ValueError):
            patch._apply_threshold(7)

    def test_add_landmark(self, patch_data_ones):
        """
        Test adding a landmark

        Args:
            patch_data_ones: Image data containing all ones

        Test Condition:
            The points in the landmark labels matrix at the given position are
                equal to the label given to them
        """

        patch = Patch(patch_data_ones, (4, 4))
        patch._mask = patch_data_ones

        position = (5, 5)
        radius = 3
        label = 7

        patch.add_landmark(position, radius, label)

        rr, cc = patch._get_circle(position, radius)

        assert np.all(patch.landmark_labels[rr, cc] == 7)

    def test_add_region(self, patch_data_zeros):
        """
        Test adding a region

        Args:
            patch_data_zeros: Image data containing all zeros

        Test Condition:
            The points in the mask at the given position are set to 1
        """

        patch = Patch(patch_data_zeros, (4, 4))
        patch._mask = patch_data_zeros

        position = (5, 5)
        radius = 3

        patch.add_region(position, radius)

        rr, cc = patch._get_circle(position, radius)

        assert np.all(patch.mask[rr, cc] == 1)

    def test_flood_add_region_new_pos(self, patch_data_zeros,
                                      patch_data_many_components):
        """
        Test using flood add with a new position.

        Args:
            patch_data_zeros: Image data with all zeros
            patch_data_many_components: Image data with many connected
                components

        Test Condition:
            The mask at the given position is 1
        """
        position = (patch_data_zeros.shape[0]//2,
                    patch_data_zeros.shape[1]//2)

        tolerance = 0.0001

        patch = Patch(patch_data_many_components, (7, 3))
        patch.mask = patch_data_zeros
        patch._old_flood_add_position = (0, 0)

        patch.flood_add_region(position, tolerance)

        assert patch.mask[position[0], position[1]] == 1

    def test_flood_add_region_old_pos(self, patch_data_zeros,
                                      patch_data_many_components):
        """
        Test using flood add with an old position.

        Args:
            patch_data_zeros: Image data with all zeros
            patch_data_many_components: Image data with many connected
                components.

        Test Condition:
            The mask at the given position is 1
        """
        position = (patch_data_zeros.shape[0]//2,
                    patch_data_zeros.shape[1]//2)

        tolerance = 0.0001

        patch = Patch(patch_data_many_components, (7, 3))
        patch.mask = patch_data_zeros
        patch._old_flood_add_position = position
        patch._old_mask = patch_data_zeros

        patch.flood_add_region(position, tolerance)

        assert patch.mask[position[0], position[1]] == 1


class TestRemoveFromMask(TestPatch):
    """
    Tests for functions that remove from the mask.
    """

    def test_clear_mask(self, patch_data_ones):
        """
        Test clearing the mask

        Args:
            patch_data_ones: Image data

        Test Condition:
            The mask is all zero's
        """

        patch = Patch(patch_data_ones, (2, 3))

        patch.clear_mask()

        assert not np.any(patch.mask)

    def test_remove_landmark(self, patch_data_ones):
        """
        Test removing pixels that were marked as landmarks

        Args:
            patch_data_ones: Image data

        Test Condition:
            The pixels in the given area are labelled as 0
        """
        patch = Patch(patch_data_ones, (3, 4))

        patch._landmark_labels = patch_data_ones

        position = (5, 5)
        radius = 3

        patch.remove_landmark(position, radius)

        rr, cc = patch._get_circle(position, radius)

        assert np.all(patch.landmark_labels[rr, cc] == 0)

    def test_remove_region(self, patch_data_ones):
        """
        Test removing a region.

        Args:
            patch_data_ones: Image data containing all ones

        Test Condition:
            The points in the mask at the given position are set to 0
        """

        patch = Patch(patch_data_ones, (4, 4))
        patch._mask = patch_data_ones

        position = (5, 5)
        radius = 3

        patch.remove_region(position, radius)

        rr, cc = patch._get_circle(position, radius)

        assert np.all(patch.mask[rr, cc] == 0)

    def test_flood_remove_region_new_pos(self, patch_data_ones,
                                         patch_data_many_components):
        """
        Test using flood remove with a new position.

        Args:
            patch_data_ones: Image data with all ones
            patch_data_many_components: Image data with many connected
                components

        Test Condition:
            The mask at the given position is 0
        """
        position = (patch_data_ones.shape[0]//2,
                    patch_data_ones.shape[1]//2)

        tolerance = 0.0001

        patch = Patch(patch_data_many_components, (7, 3))
        patch.mask = patch_data_ones
        patch._old_flood_remove_position = (0, 0)

        patch.flood_remove_region(position, tolerance)

        assert patch.mask[position[0], position[1]] == 0

    def test_flood_remove_region_old_pos(self, patch_data_ones,
                                         patch_data_many_components):
        """
        Test using flood remove with an old position.

        Args:
            patch_data_ones: Image data with all zeros
            patch_data_many_components: Image data with many connected
                components.

        Test Condition:
            The mask at the given position is 0
        """
        position = (patch_data_ones.shape[0]//2,
                    patch_data_ones.shape[1]//2)

        tolerance = 0.0001

        patch = Patch(patch_data_many_components, (7, 3))
        patch.mask = patch_data_ones
        patch._old_flood_remove_position = position
        patch._old_mask = patch_data_ones

        patch.flood_remove_region(position, tolerance)

        assert patch.mask[position[0], position[1]] == 0
