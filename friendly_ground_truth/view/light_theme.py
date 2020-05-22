"""
File Name: light_theme.py

Authors: Kyle Seidenthal

Date: 22-05-2020

Description: Light Theme

"""

from tkinter import ttk

colours = {
            "toolbar_activate": "#ffde4d",
            "toolbar_hover": "#c4c4c4"
        }

settings = {
        "PersistantToolbar.TButton": {
            "map": {
                "background": [('pressed', colours['toolbar_activate']),
                               ('disabled', colours['toolbar_activate']),
                               ('active', colours['toolbar_hover'])],
                "foreground": [],
                "relief": [('pressed', 'sunken'), ('disabled', 'sunken'),
                           ('!disabled', 'flat')]
                }

            },
        "Toolbar.TButton": {
            "map": {
                "background": [('active', colours['toolbar_hover'])],
                "relief": [('pressed', 'sunken'),
                           ]
                }
            },
        "Toolbar.TFrame": {
            "configure": {
                "borderwidth": 1,
                "relief": "raised"
                }

            }
        }

style = ttk.Style()

style.theme_create("light_theme", "clam", settings=settings)
