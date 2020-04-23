"""
File Name: overlay_ground_truth.py

Authors: Kyle Seidenthal

Date: 14-04-2020

Description: Script to display the overlay of the image and the ground truth

"""

import sys
import skimage.io as io
import skimage.segmentation as segmentation
import skimage.color as colour
import numpy as np
import matplotlib.pyplot as plt


def main(image_path, landmarks_path, mask_path, out_path=None):
    """
    Run the script using the given image and ground truth

    :param image_path: The path to the image
    :param landmarks_path: The path to the numpy labelling file
    :param mask_path: The path to the binary segmentation mask
    :returns: None
    """
    img = io.imread(image_path)
    landmarks = np.load(landmarks_path)
    mask = io.imread(mask_path)

    overlay_img = colour.label2rgb(landmarks, img, bg_label=0,
                                   colors=['red', 'green', 'blue'])

    boundary_img = segmentation.mark_boundaries(overlay_img, mask)

    if out_path is None:
        plt.imshow(boundary_img)
        plt.show()
    else:
        io.imsave(out_path, boundary_img)


if __name__ == "__main__":

    if len(sys.argv) < 4:
        print("Usage: python overlay_ground_truth.py path_to_img "
              "path_to_landmarks path_to_mask")

        sys.exit(0)

    out_path = None
    if len(sys.argv) == 5:
        out_path = sys.argv[4]

    image_path = sys.argv[1]
    landmark_path = sys.argv[2]
    mask_path = sys.argv[3]

    main(image_path, landmark_path, mask_path, out_path)
