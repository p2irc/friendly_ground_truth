"""
File Name: dark_theme.py

Authors: Kyle Seidenthal

Date: 22-05-2020

Description: Dark theme.

"""

from friendly_ground_truth.view import light_theme


colours = {
            "toolbar_activate": "#ba4100",
            "bg_level_0": "#121212",
            "fg_level_0": "#ffffff",
            "bg_level_1": "#212124",
            "fg_level_1": "#ddddeb",
            "bg_level_2": "#34353d",
            "fg_level_2": "#babbcc",
            "bg_level_3": "#454757",
            "fg_level_3": "#a1a1ab"
        }

settings = {
        "PersistantToolbar.TButton": {
            "configure": {
                    "background": colours['bg_level_2'],
                    "foreground": colours['fg_level_2'],
                    "borderwidth": 2,
                    "bordercolor": colours['bg_level_2']
                },
            "map": {
                "background": [('pressed', colours['toolbar_activate']),
                               ('disabled', colours['toolbar_activate']),
                               ('active', colours['bg_level_3'])],
                "foreground": [],
                "relief": [('pressed', 'sunken'), ('disabled', 'sunken'),
                           ('!disabled', 'flat')]
                }

            },
        "Toolbar.TButton": {
            "configure": {
                "background": colours['bg_level_2'],
                "foreground": colours['fg_level_2']
                },
            "map": {
                "background": [('active', colours['bg_level_3'])],
                "relief": [('pressed', 'sunken')]
                }
            },
        "Toolbar.TFrame": {
            "configure": {
                "borderwidth": 1,
                "bordercolor": colours['bg_level_2'],
                "background": colours['bg_level_1'],
                "foreground": colours['fg_level_1']
                }

            }

        }


style = light_theme.style


style.theme_create("dark_theme", "light_theme", settings=settings)


# Then use style.theme_use("dark_theme") in the main window
