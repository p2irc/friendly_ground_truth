"""
File Name: help_dialogs.py

Authors: Kyle Seidenthal

Date: 18-05-2020

Description: Dialogs that can be triggered from the help menu.

"""
import tkinter as tk
import webbrowser
import base64

from io import BytesIO
from tkinter import font

from friendly_ground_truth.version_info import VersionInfo
from PIL import Image, ImageTk


class AboutDialog(tk.Toplevel):
    """
    A window that displays information about the current version of the
    applciation.

    Attributes:
        {% An Attribute %}: {% Description %}
    """

    def __init__(self):
        self._base = tk.Toplevel()
        self._base.title("About")

        version_info = VersionInfo()
        current_version = version_info.get_version_string()

        latest = version_info.check_for_update()

        version_text = ("You are currently using version " +
                        current_version + " ")

        version_text += latest

        self._version_link = ("https://github.com/KyleS22/friendly_ground" +
                              "_truth/releases/latest")

        manual_text = " A user manual can be found at: "
        self._manual_link = ("https://github.com/KyleS22/friendly_ground" +
                             "_truth/wiki/User-Manual")

        bug_text = "Found a bug?  Please report it at:"
        self._bug_link = ("https://github.com/KyleS22/friendly_ground_truth" +
                          "/issues")

        self._version_label = tk.Label(self._base, text=version_text)
        self._version_label.pack(pady=15)

        if version_info.check_newer_version(version_info.
                                            get_newest_release_info()):
            self._version_link_label = tk.Label(self._base,
                                                text=self._version_link,
                                                fg="blue", cursor="hand2")
            self._version_link_label.pack(pady=15)
            self._version_link_label.bind("<Button-1>", self._on_version_click)

        self._manual_label = tk.Label(self._base, text=manual_text)
        self._manual_label.pack(pady=15)

        self._manual_link_label = tk.Label(self._base, text=self._manual_link,
                                           fg="blue", cursor="hand2")
        self._manual_link_label.pack(pady=15)
        self._manual_link_label.bind("<Button-1>", self._on_manual_click)

        self._bug_label = tk.Label(self._base, text=bug_text)
        self._bug_label.pack(pady=15)

        self._bug_link_label = tk.Label(self._base, text=self._bug_link,
                                        fg="blue", cursor="hand2")
        self._bug_link_label.pack(pady=15)
        self._bug_link_label.bind("<Button-1>", self._on_bug_click)

    def _on_version_click(self, event):
        webbrowser.open(self._version_link)

    def _on_manual_click(self, event):
        webbrowser.open(self._manual_link)

    def _on_bug_click(self, event):
        webbrowser.open(self._bug_link)


class KeyboardShortcutDialog(tk.Toplevel):
    """
    A window displaying keyboard shortcuts for all the tools.

    """

    NUM_COLS = 9

    def __init__(self, tools):
        """
        Create the dialog.

        Args:
            tools: A dictionary of tools, keyed by their id.

        Returns:
            The window.
        """

        self._base = tk.Toplevel()
        self._base.title("Keyboard Shortcuts")

        group_priorities = [(0, "Markups"), (1, "Navigation"), (2, "Undo")]

        groups = [[] for _ in group_priorities]
        groups.append([])

        for tool_id in tools.keys():
            tool = tools[tool_id]

            tool_group = tool.group

            in_priors = False

            for p in group_priorities:
                if tool_group == p[1]:
                    groups[p[0]].append(tool)
                    in_priors = True
                    continue

            if not in_priors:
                groups[-1].append(tool)

        if len(groups[-1]) == 0:
            groups.pop()

        row = 0
        for group in groups:
            name = group[0].group
            centre_col = int(min(len(group), 3) * 3 / 2) - 1
            panel = self._make_group_panel(name, centre_col)

            tool_row = 1
            tool_col = 0
            for tool in group:
                tool_col = self._make_tool_entry(tool, panel, tool_row,
                                                 tool_col)

                if tool_col >= self.NUM_COLS:
                    tool_col = 0
                    tool_row += 1

            panel.grid(row=row, column=0)
            row += 1

    def _make_tool_entry(self, tool, panel, row, column):
        """
        Create a keyboard shortcut label for the given tool.

        Args:
            tool: The tool to create the entry for.
            panel: The parent panel for the entry.
            row: The row for this tool to be put on.
            column: The column to start adding to.

        Returns:
            The next available column index.
        """
        data = Image.open(BytesIO(base64.b64decode(tool.icon_string)))
        img = ImageTk.PhotoImage(data)

        img_label = tk.Label(panel, image=img)
        img_label.image = img
        img_label.grid(row=row, column=column)
        column += 1

        shortcut_text = tool.name + " (" + tool.key_mapping + ")"
        text_label = tk.Label(panel, text=shortcut_text)
        text_label.grid(row=row, column=column)
        column += 1

        space_label = tk.Label(panel, text="    ")
        space_label.grid(row=row, column=column)
        column += 1

        return column

    def _make_group_panel(self, group, centre_col):
        """
        Create a panel for the grouping of tools.

        Args:
            group: The name of the group.
            centre_col: The column that is in the centre

        Returns:
            A panel for placing the tool icons into.
        """
        panel = tk.Frame(self._base, padx=0, pady=15)

        panel_title = tk.Label(panel, text=group)
        panel_title.grid(row=0, column=centre_col, columnspan=2)

        f = font.Font(panel_title, panel_title.cget("font"))
        f.configure(underline=True)
        f.configure(weight='bold')
        f.configure(size=16)
        panel_title.configure(font=f)

        return panel
