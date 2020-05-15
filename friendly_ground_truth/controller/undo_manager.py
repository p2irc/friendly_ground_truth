"""
File Name: undo_manager.py

Authors: Kyle Seidenthal

Date: 13-05-2020

Description: A manager for undo and redo operations

"""


class UndoManager():
    """
    Manager for undo and redo operations

    """

    MAX_SIZE = 20

    def __init__(self):

        self._undo_stack = []
        self._redo_stack = []

    def add_to_undo_stack(self, patch, operation):
        """
        Add the given image data and operation tag to the undo stack.

        Args:
            patch: The patch data for restoring later
            operation: A string tag that represents the operation taken.
                       Can be any string.
                       'threshold_adjust' is used to determine if a threshold
                       needs to be reset
                       If the word 'adjust' appears in the tag, the undo
                       operation will save a point before any adjustments were
                       made.

        Returns:
            None

        Postconditions:
            The patch data and operation are added to the undo stack.
        """

        if "threshold_adjust" == operation and len(self._undo_stack) > 0:
            if self._undo_stack[-1][1] == operation:
                return
        elif "adjust" in operation and len(self._undo_stack) > 0:
            if self._undo_stack[-1][1] == operation:
                self._undo_stack.pop()

        self._undo_stack.append((patch, operation))

        if len(self._undo_stack) > self.MAX_SIZE:
            self._undo_stack.pop(0)

    def undo(self):
        """
        Get the previous state from the undo stack.

        Returns:
            The patch data and the operation string
        """
        try:
            patch, operation = self._undo_stack.pop()
            return patch, operation

        except IndexError:
            return None, None

    def add_to_redo_stack(self, patch, operation):
        """
        Add the given operation to the redo stack.

        Args:
            patch: The patch data
            operation: The operation string.

        Returns:
            {% A thing %}
        """

        self._redo_stack.append((patch, operation))

        if len(self._redo_stack) > self.MAX_SIZE:
            self._redo_stack.pop(0)

    def redo(self):
        """
        Get the patch data and operation string for restoring.


        Returns:
            The patch data and the operation string
        """
        try:
            patch, operation = self._redo_stack.pop()
            return patch, operation
        except IndexError:
            return None, None

    def clear_undos(self):
        """
        Remove all operations from the undo and redo stacks.


        Returns:
            None

        Postconditions:
            The undo and redo stacks are empty.
        """

        self._undo_stack = []
        self._redo_stack = []
