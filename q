[1mdiff --git a/src/.friendly_ground_truth.py.swp b/src/.friendly_ground_truth.py.swp[m
[1mdeleted file mode 100644[m
[1mindex dda55f6..0000000[m
Binary files a/src/.friendly_ground_truth.py.swp and /dev/null differ
[1mdiff --git a/src/controller/.controller.py.swp b/src/controller/.controller.py.swp[m
[1mdeleted file mode 100644[m
[1mindex 532fe83..0000000[m
Binary files a/src/controller/.controller.py.swp and /dev/null differ
[1mdiff --git a/src/controller/controller.py b/src/controller/controller.py[m
[1mindex a4376be..b628b13 100644[m
[1m--- a/src/controller/controller.py[m
[1m+++ b/src/controller/controller.py[m
[36m@@ -12,6 +12,7 @@[m [mimport wx[m
 import logging[m
 [m
 from view.view import MainWindow[m
[32m+[m[32mfrom model.model import Image, Patch[m
 [m
 module_logger = logging.getLogger('friendly_gt.controller')[m
 [m
[36m@@ -59,4 +60,4 @@[m [mclass Controller:[m
 [m
             self.logger.debug("File Path: %s", pathname)[m
 [m
[31m-            # TODO: load image into model[m
[32m+[m[32m            self.image = Image(pathname)[m
[1mdiff --git a/src/model/.model.py.swp b/src/model/.model.py.swp[m
[1mdeleted file mode 100644[m
[1mindex 6c21640..0000000[m
Binary files a/src/model/.model.py.swp and /dev/null differ
[1mdiff --git a/src/model/model.py b/src/model/model.py[m
[1mindex c29ca81..cd0a2ba 100644[m
[1m--- a/src/model/model.py[m
[1m+++ b/src/model/model.py[m
[36m@@ -9,7 +9,10 @@[m [mDescription: Contains the model elements for the application[m
 [m
 """[m
 import logging[m
[31m-import skimage[m
[32m+[m[32mimport numpy as np[m
[32m+[m
[32m+[m[32mfrom skimage import io[m
[32m+[m[32mfrom skimage.util.shape import view_as_blocks[m
 [m
 module_logger = logging.getLogger('friendly_gt.model')[m
 [m
[36m@@ -19,23 +22,20 @@[m [mclass Image():[m
     Represents a loaded image[m
     """[m
 [m
[31m-    def __init__(self, path, patch_size):[m
[32m+[m[32m    def __init__(self, path):[m
         """[m
         Initialize an image object[m
 [m
         :param path: The path to the image to load[m
[31m-        :param patch_size: The size of the patches that should be made from[m
[31m-                           the image[m
         :returns: None[m
         """[m
         self.logger = logging.getLogger('friendly_gt.model.Image')[m
 [m
         self.path = path[m
[31m-        self.patch_size = patch_size[m
[31m-[m
[32m+[m[32m        self.num_patches = 10[m
         self.image = self.load_image(path)[m
[31m-        self.mask = None  # TODO: create empty mask[m
[31m-        self.patches = self.create_patches(self.image, self.patch_size)[m
[32m+[m[32m        self.mask = np.zeros(self.image.shape, dtype=bool)  # create empty mask[m
[32m+[m[32m        self.patches = self.create_patches(self.image, self.num_patches)[m
 [m
     def load_image(self, path):[m
         """[m
[36m@@ -46,17 +46,62 @@[m [mclass Image():[m
         """[m
 [m
         self.logger.debug("Loading image")[m
[31m-        pass[m
[32m+[m[32m        try:[m
[32m+[m[32m            img = io.imread(path)[m
[32m+[m[32m        except exception as e:[m
[32m+[m[32m            logger.error("That image had some issues.")[m
[32m+[m
[32m+[m[32m        return img[m
 [m
[31m-    def create_patches(self, image):[m
[32m+[m[32m    def create_patches(self, image, num_patches):[m
         """[m
         Create a list of patches from the image[m
 [m
         :param image: The image to create patches from[m
[32m+[m[32m        :param num_patches: The number of patches to create ALONG ONE DIMENSION[m
         :returns: A list of patches made from the image[m
         """[m
         self.logger.debug("Creating patches")[m
[31m-        pass[m
[32m+[m
[32m+[m[32m        # Determine padding so we can use non-overlapping patches[m
[32m+[m[32m        pad_x = (0, 0)[m
[32m+[m[32m        pad_y = (0, 0)[m
[32m+[m
[32m+[m[32m        self.logger.debug(image.shape)[m
[32m+[m
[32m+[m[32m        if image.shape[0] % num_patches is not 0:[m
[32m+[m[32m            pad_x = (0, (num_patches - (image.shape[0] % num_patches)))[m
[32m+[m
[32m+[m[32m        if image.shape[1] % num_patches is not 0:[m
[32m+[m[32m            pad_y = (0, (num_patches - (image.shape[1] % num_patches)))[m
[32m+[m
[32m+[m[32m        self.logger.debug("{}, {}".format(pad_x, pad_y))[m
[32m+[m
[32m+[m[32m        image = np.pad(image, (pad_x, pad_y, (0, 0)), 'constant',[m
[32m+[m[32m                       constant_values=(0, 0))[m
[32m+[m
[32m+[m[32m        # Get the size of each block[m
[32m+[m[32m        block_size = (image.shape[0]//num_patches,[m
[32m+[m[32m                      image.shape[1]//num_patches,[m
[32m+[m[32m                      image.shape[2])[m
[32m+[m
[32m+[m[32m        self.logger.debug(image.shape)[m
[32m+[m[32m        self.logger.debug(block_size)[m
[32m+[m
[32m+[m[32m        # Make the blocks[m
[32m+[m[32m        blocks = view_as_blocks(image, block_shape=block_size)[m
[32m+[m
[32m+[m[32m        self.logger.debug(blocks.shape)[m
[32m+[m
[32m+[m[32m        patches = [][m
[32m+[m
[32m+[m[32m        # Create a list of new patch objects for viewing[m
[32m+[m[32m        for i in range(num_patches):[m
[32m+[m[32m            for j in range(num_patches):[m
[32m+[m[32m                patch_data = blocks[i, j, 0][m
[32m+[m[32m                patches.append(Patch(patch_data, (i, j)))[m
[32m+[m
[32m+[m[32m        return patches[m
 [m
 [m
 class Patch():[m
[36m@@ -64,13 +109,17 @@[m [mclass Patch():[m
     Represents an image patch[m
     """[m
 [m
[31m-    def __init__(self, patch):[m
[32m+[m[32m    def __init__(self, patch, patch_index):[m
         """[m
         Create a patch object[m
 [m
         :param patch: The image patch to use[m
         :returns: None[m
         """[m
[31m-        self.logger = logging.getlogger('friendly_gt.model.Patch')[m
[32m+[m[32m        self.logger = logging.getLogger('friendly_gt.model.Patch')[m
         self.patch = patch[m
[31m-        self.mask = None  # TODO create empty mask[m
[32m+[m[32m        self.mask = np.zeros(self.patch.shape, dtype=bool)  # create empty mask[m
[32m+[m[32m        self.patch_index = patch_index[m
[32m+[m
[32m+[m[32m        self.logger.debug("Created patch witth index {} and shape{}"[m
[32m+[m[32m                          .format(patch_index, patch.shape))[m
[1mdiff --git a/src/view/.view.py.swp b/src/view/.view.py.swp[m
[1mdeleted file mode 100644[m
[1mindex 7c28ec4..0000000[m
Binary files a/src/view/.view.py.swp and /dev/null differ
