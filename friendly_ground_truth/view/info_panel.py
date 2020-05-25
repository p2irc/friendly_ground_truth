"""
File Name: info_panel.py

Authors: Kyle Seidenthal

Date: 15-05-2020

Description: Info Panel for tools in the UI

"""

import tkinter as tk

from tkinter import ttk


class InfoPanel(ttk.Frame):
    """
    An information panel for controlling tools.

    Attributes:
        {% An Attribute %}: {% Description %}
    """

    def __init__(self, master):

        ttk.Frame.__init__(self, master=master)

        self._master = master

        self._tool_title = "No Tool Selected"
        self._info_panel_label = ttk.Label(self,
                                           text=self._tool_title,
                                           style="InfoPanel.TLabel",
                                           anchor="center")

        self._info_panel_label.pack(side='top', fill='both')

        self._current_control = None

    def set_info_widget(self, widget, title):
        """
        Set the current info widget.

        Args:
           widget: A tkinter Frame with widgets inside
           title: The title of the tool, for updating the laebl

        Returns:
           None

        Postconditions:
            The info panel will be updated with the widget and title
        """
        self._tool_title = title

        self._info_panel_label.config(text=title)
        if self._current_control is not None:
            self._current_control.destroy()

        self._current_control = widget
        self._current_control.pack(side='top')
