"""
File Name: preferences_window.py

Authors: Kyle Seidenthal

Date: 25-05-2020

Description: A window for managing user preferences.

"""

import tkinter as tk
from tkinter import ttk


class PreferencesWindow(tk.Toplevel):
    """
    A window for managing user preferences.

    """

    def __init__(self, controller, style):
        self._base = tk.Toplevel()
        self._base.title("Preferences")

        self._frame = ttk.Frame(self._base)

        self._controller = controller

        self._preferences = self._load_preferences()

        self._preferences_panel = ttk.Frame(self._frame)
        self._theme_label = ttk.Label(self._preferences_panel, text="Theme:")

        self._theme_choice = tk.StringVar()
        self._theme_chooser = ttk.Combobox(self._preferences_panel,
                                           textvariable=self._theme_choice)

        theme_choices = ('Light', 'Dark')

        theme_pref = theme_choices.index(self._preferences['theme'])

        self._theme_chooser['values'] = theme_choices
        self._theme_chooser.current(theme_pref)

        self._theme_label.grid(row=0, column=0)
        self._theme_chooser.grid(row=0, column=1)

        self._preferences_panel.pack(fill='both', expand=True, padx=10,
                                     pady=15)

        self._button_panel = ttk.Frame(self._frame)

        apply_button = ttk.Button(self._button_panel, text="Apply",
                                  command=self._on_apply)

        cancel_button = ttk.Button(self._button_panel, text="Cancel",
                                   command=self._on_cancel)

        cancel_button.pack(side="left")
        apply_button.pack(side="right")

        self._button_panel.pack(fill='both', expand=True)
        self._frame.pack(fill='both', expand=True)

    def _on_apply(self):

        preferences = {}

        theme = self._theme_choice.get()
        preferences['theme'] = str(theme)

        self._preferences = preferences

        self._controller.set_preferences(preferences)
        self._controller.save_preferences(preferences)

    def _on_cancel(self):
        self._base.destroy()

    def _load_preferences(self):
        return self._controller.load_preferences()
