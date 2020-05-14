"""
File Name: tools.py

Authors: Kyle Seidenthal

Date: 11-05-2020

Description: Definitions of tools that can be used in Friendly Ground Truth

"""
import logging

from friendly_ground_truth.view.icons.icon_strings import (threshold_icon,
                                                           add_region_icon,
                                                           remove_region_icon,
                                                           no_root_icon,
                                                           flood_add_icon,
                                                           flood_remove_icon,
                                                           prev_patch_icon,
                                                           next_patch_icon,
                                                           undo_icon,
                                                           redo_icon)

module_logger = logging.getLogger('friendly_gt.controller.tools')


class FGTTool():
    """
    A class representing a tool that can be used on the image.

    Attributes:
        name: The name of the tool
        icon_string: A 64 bit encoded string representing an icon image
        id: A unique id for the tool
    """

    def __init__(self, name, icon_string, id, cursor='none'):
        """
        Initialize the object

        Args:
            name: The name of the tool
            icon_string: A bytestring representing the icon for the tool
            id: A unique id for the tool
            cursor: The default cursor for this tool.  Default value is 'none'
            patch: The current patch to operate on
        """
        self._logger = logging\
            .getLogger('friendly_gt.controller.tools.FGTTool')

        self._name = name
        self._icon_string = icon_string
        self._id = id
        self._cursor = cursor

    @property
    def name(self):
        return self._name

    @property
    def icon_string(self):
        return self._icon_string

    @icon_string.setter
    def icon_string(self, string):
        self._icon_string = string

    @property
    def id(self):
        return self._id

    @property
    def cursor(self):
        return self._cursor

    @property
    def patch(self):
        return self._patch

    @patch.setter
    def patch(self, patch):
        self._patch = patch


class ThresholdTool(FGTTool):
    """
    Tool representing a threshold action.

    Attributes:
        threshold: The value of the threshold. Between 0 and 1.
        increment: The amount to change the threshold by when adjusting
    """

    def __init__(self):

        super(ThresholdTool, self)\
            .__init__("Threshold Tool", threshold_icon, 1, 'arrow')

        self._logger = logging\
            .getLogger('friendly_gt.controller.tools.ThresholdTool')

        self._threshold = 0
        self._increment = 0.01
        self._patch = None

    @property
    def threshold(self):
        return self._threshold

    @threshold.setter
    def threshold(self, value):
        if value <= 1 and value >= 0:
            self._threshold = value
            self._patch.threshold = value

    @property
    def increment(self):
        return self._increment

    @increment.setter
    def increment(self, value):
        self._increment = value

    @FGTTool.patch.setter
    def patch(self, patch):
        self._patch = patch
        self._threshold = patch.threshold

    def adjust_threshold(self, direction):
        """
        Adjust the current threshold

        Args:
            direction: An integer, positive indicates increasing threshold,
                       negative idicates decreasing threshold

        Returns:
            None, the patch threshold will be set accordingly
        """

        if direction > 0:
            self.threshold += self.increment
        else:
            self.threshold -= self.increment


class AddRegionTool(FGTTool):
    """
    A tool acting as a paint brush for adding regions to the mask

    Attributes:
        brush_radius: The current radius of the brush
    """

    def __init__(self):
        super(AddRegionTool, self)\
            .__init__("Add Region Tool", add_region_icon, 2, 'brush')

        self._logger = logging\
            .getLogger('friendly_gt.controller.tools.AddRegionTool')

        self._brush_radius = 15

    @property
    def brush_radius(self):
        return self._brush_radius

    @brush_radius.setter
    def brush_radius(self, value):
        if value >= 0:
            self._brush_radius = value

    def draw(self, position):
        """
        Draw a circle at the given position.  Uses the brush_radius property.

        Args:
            position: (x, y) coordinates to draw at.

        Returns:
            None

        Postcondition:
            The mask at the given position will be filled in.
        """

        self.patch.add_region(position, self.brush_radius)


class RemoveRegionTool(FGTTool):
    """
    A tool acting as a paint brush for removing regions from the mask

    Attributes:
        brush_radius: The current radius of the brush
    """

    def __init__(self):
        super(RemoveRegionTool, self)\
            .__init__("Remove Region Tool", remove_region_icon, 3, 'brush')

        self._logger = logging\
            .getLogger('friendly_gt.controller.tools.RemoveRegionTool')

        self._brush_radius = 15

    @property
    def brush_radius(self):
        return self._brush_radius

    @brush_radius.setter
    def brush_radius(self, value):
        if value >= 0:
            self._brush_radius = value

    def draw(self, position):
        """
        Remove a circle at the given position.  Uses the brush_radius property.

        Args:
            position: (x, y) coordinates to draw at.

        Returns:
            None

        Postcondition:
            The mask at the given position will be removed.
        """

        self.patch.remove_region(position, self.brush_radius)


class NoRootTool(FGTTool):
    """
    A tool that marks a patch as having no foreground.
    """

    def __init__(self):
        super(NoRootTool, self)\
            .__init__("No Root Tool", no_root_icon, 4, 'none')

        self._logger = logging\
            .getLogger('friendly_gt.controller.tools.NoRootTool')

    def no_root(self):
        """
        Clear the mask for this patch.


        Returns:
            None

        Postconditions:
            The mask for this patch is cleared.
        """
        self.patch.clear_mask()


class FloodAddTool(FGTTool):
    """
    A tool that allows adding a region based on pixel tolerance.

    Attributes:
        tolerance: The tolerance for pixels to add to the region.
    """

    def __init__(self):
        super(FloodAddTool, self)\
            .__init__("Flood Add Tool", flood_add_icon, 5, 'cross')

        self._logger = logging\
            .getLogger('friendly_gt.controller.tools.FloodAddTool')

        self._tolerance = 0.05

    @property
    def tolerance(self):
        return self._tolerance

    @tolerance.setter
    def tolerance(self, value):
        if value >= 0:
            self._tolerance = value

    def add_region(self, position):
        """
        Add a region at the given position, using the tolerance attribute.

        Args:
            position: (x, y) coordinates to start the flood.

        Returns:
            None

        Postconditions:
            A region will be added to the mask that matches the flooded region.
        """

        self.patch.flood_add(position, self.tolerance)


class FloodRemoveTool(FGTTool):
    """
    A tool that allows removing a region based on pixel tolerance.

    Attributes:
        tolerance: The tolerance for pixels to remove from the region.
    """

    def __init__(self):
        super(FloodRemoveTool, self)\
            .__init__("Flood Remove Tool", flood_remove_icon, 6, 'cross')

        self._logger = logging\
            .getLogger('friendly_gt.controller.tools.FloodRemoveTool')

        self._tolerance = 0.05

    @property
    def tolerance(self):
        return self._tolerance

    @tolerance.setter
    def tolerance(self, value):
        if value > 0:
            self._tolerance = value

    def remove_region(self, position):
        """
        Remove a region at the given position, using the tolerance attribute.

        Args:
            position: (x, y) coordinates to start the flood.

        Returns:
            None

        Postconditions:
            A region will be removed to the mask that matches the
                flooded region.
        """

        self.patch.flood_remove(position, self.tolerance)


class PreviousPatchTool(FGTTool):
    """
    A Tool that moves to the previous patch for the current image.

    Attributes:
        image: The image to operate on
    """

    def __init__(self, image):
        """
        Create the tool.

        Args:
            image: The image that is being operated on.

        Returns:
            A tool object
        """
        super(PreviousPatchTool, self)\
            .__init__("Previous Patch", prev_patch_icon, 7, 'none')

        self._image = image

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, image):
        self._image = image

    def prev_patch(self, current_patch_num):
        """
        Move to the previous patch in the image.

        Args:
            current_patch_num: The index of the current patch.

        Returns:
            (patch, current_patch_index) if there is a previous patch
            (None, -1) if there is not a previous patch
        """

        patches = self._image.patches

        prev_index = current_patch_num - 1

        if prev_index >= 0:
            return patches[prev_index], prev_index

        else:
            return None, -1

class NextPatchTool(FGTTool):
    """
    A Tool that moves to the next patch for the current image.

    Attributes:
        image: The image to operate on
    """

    def __init__(self, image):
        """
        Create the tool.

        Args:
            image: The image that is being operated on.

        Returns:
            A tool object
        """
        super(NextPatchTool, self)\
            .__init__("Next Patch", next_patch_icon, 8, 'none')

        self._image = image

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, image):
        self._image = image

    def next_patch(self, current_patch_num):
        """
        Move to the next patch in the image.

        Args:
            current_patch_num: The index of the current patch.

        Returns:
            (patch, current_patch_index) if there is a next patch
            (None, -1) if there is not a next patch
        """

        patches = self._image.patches

        next_index = current_patch_num + 1

        if next_index < len(patches):
            return patches[next_index], next_index

        else:
            return None, -1


class UndoTool(FGTTool):
    """
    A tool for undoing mistakes.

    Attributes:
        undo_manager: A manager for undo operations
    """

    def __init__(self, undo_manager):
        """
        Initialize the tool

        Args:
            undo_manager: The manager for undo and redo operations

        Returns:
            A tool object
        """
        super(UndoTool, self)\
            .__init__("Undo", undo_icon, 9, 'none')

        self._undo_manager = undo_manager

    def undo(self):
        """
        Undo the last operation.


        Returns:
            The patch data and the operation string
        """

        return self.undo_manager.undo()


class RedoTool(FGTTool):
    """
    A tool for redoing undid mistakes.

    Attributes:
        undo_manager: A manager for undo operations
    """

    def __init__(self, undo_manager):
        """
        Initialize the tool

        Args:
            undo_manager: The manager for undo and redo operations

        Returns:
            A tool object
        """
        super(RedoTool, self)\
            .__init__("Redo", redo_icon, 10, 'none')

        self._undo_manager = undo_manager

    def redo(self):
        """
        Redo the undone last operation.


        Returns:
            The patch data and the operation string
        """

        return self.undo_manager.redo()
