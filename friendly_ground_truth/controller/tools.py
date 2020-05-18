"""
File Name: tools.py

Authors: Kyle Seidenthal

Date: 11-05-2020

Description: Definitions of tools that can be used in Friendly Ground Truth

"""
import logging
import copy
import tkinter as tk

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
        persistant: Whether the tool stays activated when it has been activated
        key_mapping: The keyboard shortcut string for this tool
        activation_callback: A function to call when the activate functiion is
                             finished
        info_widget: A tkinter widget for controlling this tool from an info
                     panel
    """

    def __init__(self, name, icon_string, id,  undo_manager,
                 key_mapping, cursor='none', persistant=True,
                 activation_callback=None, group=None):
        """
        Initialize the object

        Args:
            name: The name of the tool
            icon_string: A bytestring representing the icon for the tool
            id: A unique id for the tool
            cursor: The default cursor for this tool.  Default value is 'none'
            undo_manager: The controller's undo manager
            key_mapping: The keyboard shortcut string for this tool
            activation_callback: A function to call when the activate function
                                 is finished
            group: If this tool should be grouped with other tools, this string
                   identifies what group it is a part of.
        """
        self._logger = logging\
            .getLogger('friendly_gt.controller.tools.FGTTool')

        self._name = name
        self._icon_string = icon_string
        self._id = id
        self._cursor = cursor
        self._undo_manager = undo_manager
        self._key_mapping = key_mapping
        self._activation_callback = activation_callback
        self._persistant = persistant
        self._can_undo = True
        self._observers = []
        self._group = group

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

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, image):
        self._image = image

    @property
    def persistant(self):
        return self._persistant

    @property
    def key_mapping(self):
        return self._key_mapping

    @property
    def group(self):
        return self._group

    def get_info_widget(self, parent):
        """
        Get the widget that controls this tool in the UI.

        Args:
            parent: The parent for the widget.

        Returns:
            The tkinter Frame widget for this tool.
        """
        self._info_widget = tk.Frame(parent, padx=0, pady=15)
        return self._info_widget

    def lock_undos(self):
        """
        Make sure that undoing this action does not accidentally add it to the
        undo stack again.


        Returns:
            None

        Postconditions:
            The _can_undo variable is set to False
        """
        self._can_undo = False

    def unlock_undos(self):
        """
        Unlock undos so operations can be added to the undo stack.


        Returns:
            None

        Postconditions:
            The _can_undo variable is set to True
        """
        self._can_undo = True

    def destroy_info_widget(self):
        """
        Set info widget attributes to none to avoid tkinter errors.


        Returns:
            None
        """
        pass

    def on_adjust(self, direction):
        """
        What happens when the tool is adjusted.

        Args:
            direction: An integer, positive is up, negative is down

        Returns:
            None
        """
        pass

    def on_click(self, position):
        """
        What happens for mouse clicks.

        Args:
            position: The position of the click

        Returns:
            None
        """
        pass

    def on_drag(self, position):
        """
        What happens for click and drag.

        Args:
            position: The position of the mouse

        Returns:
            None
        """
        pass

    def on_activate(self, current_patch_num):
        """
        What happens when the tool is activated.

        Args:
            current_patch_num: The index of the current patch in the patches
                               list
        Returns:
            None

        Postconditions:
            The activation callback may be called.
        """
        pass

    def bind_to(self, callback):
        """
        Add the callback to the list of observers for updates.

        Args:
            callback: The function to call when things change.
                        It should have no parameters, it just says that
                        something about the image has changed.
        Returns:
            None

        Postconditions:
            The callback is added to the list of observers.
        """
        self._observers.append(callback)

    def _notify_observers(self):
        """
        Notify observers of changes made.


        Returns:
            None

        Postconditions:
            Observer callbacks are called.
        """
        for ob in self._observers:
            ob()


class ThresholdTool(FGTTool):
    """
    Tool representing a threshold action.

    Attributes:
        threshold: The value of the threshold. Between 0 and 1.
        increment: The amount to change the threshold by when adjusting
    """

    def __init__(self, undo_manager):

        super(ThresholdTool, self)\
            .__init__("Threshold Tool", threshold_icon, 1,
                      undo_manager, "t", cursor='arrow', persistant=True,
                      activation_callback=None, group="Markups")

        self._logger = logging\
            .getLogger('friendly_gt.controller.tools.ThresholdTool')

        self._threshold = 0
        self._increment = 0.01
        self._patch = None

        self._threshold_slider_var = None
        self._threshold_slider = None
        self._new_patch = False

    @property
    def threshold(self):
        return self._threshold

    @threshold.setter
    def threshold(self, value):
        if value <= 1 and value >= 0:

            self._threshold = value
            if not self._new_patch:
                self._patch.threshold = value

                if self._can_undo:
                    self._undo_manager.\
                        add_to_undo_stack(copy.deepcopy(self.patch),
                                          'threshold_adjust')

            if self._threshold_slider is not None:
                self._threshold_slider_var = value
                self._threshold_slider.set(value)

            self._logger.debug('Threshold drawing image')
            self._notify_observers()
            self._new_patch = False

    @property
    def increment(self):
        return self._increment

    @increment.setter
    def increment(self, value):
        self._increment = value

    @property
    def patch(self):
        return self._patch

    @patch.setter
    def patch(self, patch):

        if self.patch is None or patch.patch_index != self.patch.patch_index:
            self._new_patch = True

        self._patch = patch
        self._slider_init = False

        self._threshold = patch.threshold

    def get_info_widget(self, parent):
        """
        Get the widget that controls this tool in the info panel.

        Args:
            parent: The parent tkinter object.

        Returns:
            The widget.
        """
        self.lock_undos()
        super().get_info_widget(parent)

        self._threshold_slider_var = tk.DoubleVar()

        self._threshold_slider = tk.Scale(self._info_widget,
                                          from_=0.00,
                                          to=1.00,
                                          tickinterval=0.50,
                                          resolution=0.01,
                                          length=200,
                                          variable=self._threshold_slider_var,
                                          orient='horizontal',
                                          command=self._on_threshold_slider)

        self._threshold_slider.set(self._threshold)
        self._threshold_slider.pack(side='top')

        self.unlock_undos()

        return self._info_widget

    def destroy_info_widget(self):
        """
        Destroy the info widget.


        Returns:
            None

        Postconditions:
            The info widget properties are set to None.
        """
        self._threshold_slider = None
        self._threshold_slider_var = None

    def _on_threshold_slider(self, value):
        """
        Called when the threshold slider is moved.

        Args:
            value: The value of the slider

        Returns:
            None

        Postconditions:
            The threshold for the patch is udpated accordingly.
        """
        if self._slider_init:
            self.threshold = float(value)

        self._slider_init = True

    def _adjust_threshold(self, direction):
        """
        Adjust the current threshold

        Args:
            direction: An integer, positive indicates increasing threshold,
                       negative idicates decreasing threshold

        Returns:
            None, the patch threshold will be set accordingly
        """
        # Note inverted direction, it is more intuitive to increase the region,
        # than to increase the threshold
        if direction < 0:
            self.threshold += self.increment
        else:
            self.threshold -= self.increment

    def on_adjust(self, direction):
        """
        Adjust the threshold in the correct direction

        Args:
            direction: The direction, an integer
                       Negative is down, positive is up

        Returns:
            None
        """
        self._adjust_threshold(direction)


class AddRegionTool(FGTTool):
    """
    A tool acting as a paint brush for adding regions to the mask

    Attributes:
        brush_radius: The current radius of the brush
    """

    def __init__(self, undo_manager):
        super(AddRegionTool, self)\
            .__init__("Add Region Tool", add_region_icon, 2,
                      undo_manager, "a", cursor='brush', persistant=True,
                      group="Markups")

        self._logger = logging\
            .getLogger('friendly_gt.controller.tools.AddRegionTool')

        self._brush_radius = 15
        self._brush_observers = []
        self._brush_sizer = None

    @property
    def brush_radius(self):
        return self._brush_radius

    @brush_radius.setter
    def brush_radius(self, value):
        if value >= 0:
            self._brush_radius = value

            for ob in self._brush_observers:
                ob(self._brush_radius)

            if self._brush_sizer is not None:
                self._brush_sizer_var.set(value)

    def get_info_widget(self, parent):
        """
        Get the widget that controls this tool in the info panel.

        Args:
            parent: The parent tkinter object.

        Returns:
            The widget.
        """
        super().get_info_widget(parent)

        self._brush_size_panel = tk.Frame(self._info_widget,
                                          padx=0, pady=15)

        self._brush_size_label = tk.Label(self._brush_size_panel,
                                          text="Brush Size")

        self._brush_sizer_var = tk.IntVar()
        self._brush_sizer_var.set(self._brush_radius)
        self._brush_sizer_var.trace('w', self._on_brush_sizer)

        self._brush_sizer = tk.Spinbox(self._brush_size_panel,
                                       from_=0,
                                       to=64,
                                       width=17,
                                       textvariable=self._brush_sizer_var)

        self._brush_size_label.pack(side='left')
        self._brush_sizer.pack(side='left')

        self._brush_size_panel.pack(side='top')

        return self._info_widget

    def _on_brush_sizer(self, a, b, c):
        """
        Called when the brush sizer is updated.

        Args:
            value: The value of the sizer.

        Returns:
            None

        Postconditions:
            The brush radius is udpated accordingly.
        """

        val = self._brush_sizer_var.get()
        self.brush_radius = val

    def on_adjust(self, direction):
        """
        Adust the brush size according to the direction.

        Args:
            direction: An integer, positive means up, negative means down.

        Returns:
            None
        """
        if direction > 0:
            self.brush_radius += 1
        else:
            self.brush_radius -= 1

    def bind_brush(self, callback):
        """
        Subscribe to brush radius notifications.

        Args:
            callback: The function to call when the brush radius changes.

        Returns:
            None
        """
        self._brush_observers.append(callback)

    def on_click(self, position):
        """
        What to do on mouse clicks.

        Args:
            position: The position of the mouse.

        Returns:
            None
        """
        self._undo_manager.add_to_undo_stack(copy.deepcopy(self.patch),
                                             "add_region")

        self._draw(position)

    def on_drag(self, position):
        """
        What to do when clicking and dragging

        Args:
            position: The position of the mouse.

        Returns:
            None
        """
        self._undo_manager.add_to_undo_stack(copy.deepcopy(self.patch),
                                             "add_region_adjust")
        self._draw(position)

    def _draw(self, position):
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
        self._notify_observers()


class RemoveRegionTool(FGTTool):
    """
    A tool acting as a paint brush for removing regions from the mask

    Attributes:
        brush_radius: The current radius of the brush
    """

    def __init__(self, undo_manager):
        super(RemoveRegionTool, self)\
            .__init__("Remove Region Tool", remove_region_icon, 3,
                      undo_manager, "r", cursor="brush", persistant=True,
                      group="Markups")

        self._logger = logging\
            .getLogger('friendly_gt.controller.tools.RemoveRegionTool')

        self._brush_radius = 15
        self._brush_observers = []
        self._brush_sizer = None

    @property
    def brush_radius(self):
        return self._brush_radius

    @brush_radius.setter
    def brush_radius(self, value):
        if value >= 0:
            self._brush_radius = value

            for ob in self._brush_observers:
                ob(self._brush_radius)

            if self._brush_sizer is not None:
                self._brush_sizer_var.set(value)

    def get_info_widget(self, parent):
        """
        Get the widget that controls this tool in the info panel.

        Args:
            parent: The parent tkinter object.

        Returns:
            The widget.
        """
        super().get_info_widget(parent)

        self._brush_size_panel = tk.Frame(self._info_widget,
                                          padx=0, pady=15)

        self._brush_size_label = tk.Label(self._brush_size_panel,
                                          text="Brush Size")

        self._brush_sizer_var = tk.IntVar()
        self._brush_sizer_var.set(self._brush_radius)
        self._brush_sizer_var.trace('w', self._on_brush_sizer)

        self._brush_sizer = tk.Spinbox(self._brush_size_panel,
                                       from_=0,
                                       to=64,
                                       width=17,
                                       textvariable=self._brush_sizer_var)

        self._brush_size_label.pack(side='left')
        self._brush_sizer.pack(side='left')

        self._brush_size_panel.pack(side='top')

        return self._info_widget

    def _on_brush_sizer(self, a, b, c):
        """
        Called when the brush sizer is updated.

        Args:
            value: The value of the sizer.

        Returns:
            None

        Postconditions:
            The brush radius is udpated accordingly.
        """

        val = self._brush_sizer_var.get()
        self.brush_radius = val

    def on_adjust(self, direction):
        """
        Adust the brush size according to the direction.

        Args:
            direction: An integer, positive means up, negative means down.

        Returns:
            None
        """
        if direction > 0:
            self.brush_radius += 1
        else:
            self.brush_radius -= 1

    def bind_brush(self, callback):
        """
        Subscribe to brush radius notifications.

        Args:
            callback: The function to call when the brush radius changes.

        Returns:
            None
        """
        self._brush_observers.append(callback)

    def on_click(self, position):
        """
        What to do on mouse clicks.

        Args:
            position: The position of the mouse.

        Returns:
            None
        """
        self._undo_manager.add_to_undo_stack(copy.deepcopy(self.patch),
                                             "remove_region")

        self._draw(position)

    def on_drag(self, position):
        """
        What to do when clicking and dragging

        Args:
            position: The position of the mouse.

        Returns:
            None
        """
        self._undo_manager.add_to_undo_stack(copy.deepcopy(self.patch),
                                             "remove_region_adjust")
        self._draw(position)

    def _draw(self, position):
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
        self._notify_observers()


class NoRootTool(FGTTool):
    """
    A tool that marks a patch as having no foreground.
    """

    def __init__(self, undo_manager, next_patch_function):
        """
        Create the tool

        Args:
            undo_manager: The undo manager
            next_patch_function: The function to call to go to the next patch.
                                 Must have a patch and index parameter

        Returns:
            {% A thing %}
        """
        super(NoRootTool, self)\
            .__init__("No Root Tool", no_root_icon, 4,
                      undo_manager, "x", cursor='arrow', persistant=False,
                      activation_callback=next_patch_function,
                      group="Navigation")

        self._logger = logging\
            .getLogger('friendly_gt.controller.tools.NoRootTool')

    def on_activate(self, current_patch_num):
        """
        What happens when the tool is activated.

        Args:
            current_patch_num: The index of the current patch in the patches
                               list
        Returns:
            None

        Postconditions:
            The foreground is removed from the patch, and the next patch is
            displayed.
        """
        self._undo_manager.add_to_undo_stack(copy.deepcopy(self.patch),
                                             "no_root")

        self._no_root()
        patch, index = self._next_patch(current_patch_num)

        self._activation_callback(patch, index)

    def _no_root(self):
        """
        Clear the mask for this patch.


        Returns:
            None

        Postconditions:
            The mask for this patch is cleared.
        """
        self.patch.clear_mask()

    def _next_patch(self, current_patch_num):
        """
        Move to the next patch if it exists.

        Args:
            current_patch_num: The index of the current patch in the patches
                               list.

        Returns:
            A (patch, patch_num) tuple if there is a next patch.
            (None, -1) if there is not a next patch
        """
        patches = self._image.patches

        next_index = current_patch_num + 1

        if next_index < len(patches):
            self._undo_manager.clear_undos()
            return patches[next_index], next_index

        else:
            return None, -1


class FloodAddTool(FGTTool):
    """
    A tool that allows adding a region based on pixel tolerance.

    Attributes:
        tolerance: The tolerance for pixels to add to the region.
        increment: The amount that the tolerance increases by when using the
                   adjust method
    """

    def __init__(self, undo_manager):
        super(FloodAddTool, self)\
            .__init__("Flood Add Tool", flood_add_icon, 5,
                      undo_manager, "f", cursor='crosshair', persistant=True,
                      group="Markups")

        self._logger = logging\
            .getLogger('friendly_gt.controller.tools.FloodAddTool')

        self._tolerance = 0.05
        self._increment = 0.01

        self._prev_position = None
        self._flood_slider = None
        self._flood_slider_var = None

    @property
    def tolerance(self):
        return self._tolerance

    @tolerance.setter
    def tolerance(self, value):
        if value >= 0:
            self._tolerance = value

            if self._flood_slider is not None:
                self._flood_slider_var = value
                self._flood_slider.set(value)

            self._add_region(self._prev_position)
            self._notify_observers()

    @property
    def increment(self):
        return self._increment

    @increment.setter
    def increment(self, value):
        self._increment = value

    @property
    def patch(self):
        return self._patch

    @patch.setter
    def patch(self, patch):
        self._patch = patch
        self._tolerance = 0.05
        self._prev_position = None

    def on_click(self, position):
        """
        When the mouse is clicked, start the flood at the position/

        Args:
            position: The (x, y) coordinates of the place to start the flood.

        Returns:
            None
        """
        self._prev_position = position
        self._undo_manager.add_to_undo_stack(copy.deepcopy(self.patch),
                                             'flood_add')
        self._add_region(position)

    def on_adjust(self, direction):
        """
        When the tool is adjusted, the tolerance is changed.

        Args:
            direction: An integer, positive means up, negative means down.

        Returns:
            None
        """

        if direction > 0:
            self.tolerance += self.increment
        else:
            self.tolerance -= self.increment

        self._add_region(self._prev_position)

    def _add_region(self, position):
        """
        Add a region at the given position, using the tolerance attribute.

        Args:
            position: (x, y) coordinates to start the flood.

        Returns:
            None

        Postconditions:
            A region will be added to the mask that matches the flooded region.
        """
        if position is None:
            return

        self.patch.flood_add_region(position, self.tolerance)
        self._notify_observers()

    def get_info_widget(self, parent):
        """
        Get the widget that controls this tool in the info panel.

        Args:
            parent: The parent tkinter object.

        Returns:
            The widget.
        """
        super().get_info_widget(parent)

        self._flood_slider_var = tk.DoubleVar()

        self._flood_slider = tk.Scale(self._info_widget,
                                      from_=0.00,
                                      to=1.00,
                                      tickinterval=0.50,
                                      resolution=0.01,
                                      length=200,
                                      variable=self.
                                      _flood_slider_var,
                                      orient='horizontal',
                                      command=self._on_flood_slider)

        self._flood_slider.set(self._tolerance)
        self._flood_slider.pack(side='top')

        return self._info_widget

    def _on_flood_slider(self, value):
        """
        Called when the flood slider is moved.

        Args:
            value: The value of the slider

        Returns:
            None

        Postconditions:
            The tolerance for the patch is udpated accordingly.
        """
        self.tolerance = float(value)


class FloodRemoveTool(FGTTool):
    """
    A tool that allows removing a region based on pixel tolerance.

    Attributes:
        tolerance: The tolerance for pixels to remove from the region.
    """

    def __init__(self, undo_manager):
        super(FloodRemoveTool, self)\
            .__init__("Flood Remove Tool", flood_remove_icon, 6,
                      undo_manager, "l", cursor='crosshair', persistant=True,
                      group="Markups")

        self._logger = logging\
            .getLogger('friendly_gt.controller.tools.FloodRemoveTool')

        self._tolerance = 0.05
        self._increment = 0.01

        self._prev_position = None
        self._flood_slider = None
        self._flood_slider_var = None

    @property
    def tolerance(self):
        return self._tolerance

    @tolerance.setter
    def tolerance(self, value):
        if value > 0:
            self._tolerance = value

            if self._flood_slider is not None:
                self._flood_slider_var = value
                self._flood_slider.set(value)

            self._remove_region(self._prev_position)
            self._notify_observers()

    @property
    def increment(self):
        return self._increment

    @increment.setter
    def increment(self, value):
        self._increment = value

    @property
    def patch(self):
        return self._patch

    @patch.setter
    def patch(self, patch):
        self._patch = patch
        self._tolerance = 0.05
        self._prev_position = None

    def on_click(self, position):
        """
        When the mouse is clicked, start the flood at the position.

        Args:
            position: The (x, y) coordinates of the place to start the flood.

        Returns:
            None
        """
        self._prev_position = position
        self._undo_manager.add_to_undo_stack(copy.deepcopy(self.patch),
                                             'flood_remove')
        self._remove_region(position)

    def on_adjust(self, direction):
        """
        When the tool is adjusted, the tolerance is changed.

        Args:
            direction: An integer, positive means up, negative means down.

        Returns:
            None
        """

        if direction > 0:
            self.tolerance += self.increment
        else:
            self.tolerance -= self.increment

        self._remove_region(self._prev_position)

    def _remove_region(self, position):
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

        if position is None:
            return

        self.patch.flood_remove_region(position, self.tolerance)
        self._notify_observers()

    def get_info_widget(self, parent):
        """
        Get the widget that controls this tool in the info panel.

        Args:
            parent: The parent tkinter object.

        Returns:
            The widget.
        """
        super().get_info_widget(parent)

        self._flood_slider_var = tk.DoubleVar()

        self._flood_slider = tk.Scale(self._info_widget,
                                      from_=0.00,
                                      to=1.00,
                                      tickinterval=0.50,
                                      resolution=0.01,
                                      length=200,
                                      variable=self.
                                      _flood_slider_var,
                                      orient='horizontal',
                                      command=self._on_flood_slider)

        self._flood_slider.set(self._tolerance)
        self._flood_slider.pack(side='top')

        return self._info_widget

    def _on_flood_slider(self, value):
        """
        Called when the flood slider is moved.

        Args:
            value: The value of the slider

        Returns:
            None

        Postconditions:
            The tolerance for the patch is udpated accordingly.
        """
        self.tolerance = float(value)


class PreviousPatchTool(FGTTool):
    """
    A Tool that moves to the previous patch for the current image.

    Attributes:
        image: The image to operate on
    """

    def __init__(self, undo_manager, prev_patch_function):
        """
        Create the tool.

        Args:
            undo_manager: The undo manager
            prev_patch_function: A function callback that takes in a patch and
                                 patch index representing the next patch

        Returns:
            A tool object
        """
        super(PreviousPatchTool, self)\
            .__init__("Previous Patch", prev_patch_icon, 7,
                      undo_manager, "Left", cursor='arrow',
                      persistant=False,
                      activation_callback=prev_patch_function,
                      group="Navigation")

    def on_activate(self, current_patch_num):
        """
        When the tool is activated, move to the previous patch.

        Args:
            current_patch_num: The index of the current patch in the patches
                               list

        Returns:
            None
        """
        patch, index = self._prev_patch(current_patch_num)
        self._activation_callback(patch, index)

    def _prev_patch(self, current_patch_num):
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
    """

    def __init__(self, undo_manager, next_patch_function):
        """
        Create the tool.

        Args:
            undo_manager: The undo_manager for this tool.
            next_patch_function: A function callback that takes in a patch and
                                 index
        Returns:
            A tool object
        """
        super(NextPatchTool, self)\
            .__init__("Next Patch", next_patch_icon, 8,
                      undo_manager, "Right", cursor='arrow',
                      persistant=False,
                      activation_callback=next_patch_function,
                      group="Navigation")

    def on_activate(self, current_patch_num):
        """
        When the tool is activated, move to the next patch.

        Args:
            current_patch_num: The index of the current patch in the patches
                               list

        Returns:
            None
        """
        patch, index = self._next_patch(current_patch_num)
        self._activation_callback(patch, index)

    def _next_patch(self, current_patch_num):
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
    """

    def __init__(self, undo_manager, undo_callback):
        """
        Initialize the tool

        Args:
            undo_manager: The manager for undo and redo operations
            undo_callback: A function taking in a patch object and string tag
                           to call when the undo action is taken.
        Returns:
            A tool object
        """
        super(UndoTool, self)\
            .__init__("Undo", undo_icon, 9, undo_manager,
                      "CTRL+z", cursor='arrow', persistant=False,
                      activation_callback=undo_callback, group="Undo")

    def on_activate(self, current_patch_num):
        """
        Activate the undo tool.

        Args:
            current_patch_num: The current patch index in the patches list.

        Returns:
            The patch data and operation string.

        Postconditions:
            The last action is undone and put on the redo stack.
        """
        patch, string = self._undo()
        self._activation_callback(patch, string)
        self._notify_observers()

    def _undo(self):
        """
        Undo the last operation.


        Returns:
            The patch data and the operation string
        """
        return self._undo_manager.undo()


class RedoTool(FGTTool):
    """
    A tool for redoing undid mistakes.
    """

    def __init__(self, undo_manager, redo_callback):
        """
        Initialize the tool

        Args:
            undo_manager: The manager for undo and redo operations
            redo_callback: A function taking in a patch and string to call
                           when the undo action is taken.
        Returns:
            A tool object
        """
        super(RedoTool, self)\
            .__init__("Redo", redo_icon, 10, undo_manager, "CTRL+r",
                      cursor='arrow', persistant=False,
                      activation_callback=redo_callback, group="Undo")

    def on_activate(self, current_patch_num):
        """
        Activate the redo tool.

        Args:
            current_patch_num: The current patch index in the patches list.

        Returns:
            The patch data and operation string

        Postconditions:
            The last undone action is redone and put on the undo stack.
        """
        patch, string = self._redo()
        self._activation_callback(patch, string)
        self._notify_observers()

    def _redo(self):
        """
        Redo the undone last operation.


        Returns:
            The patch data and the operation string
        """
        return self._undo_manager.redo()
