"""
File Name: fgt_canvas.py

Authors: Kyle Seienthal

Date: 13-05-2020

Description: Canvas widget for displaying and interacting with images.


Code largely adapted from https://stackoverflow.com/a/48137257
"""
import math
import warnings
import tkinter as tk

import threading

from tkinter import ttk
from PIL import Image, ImageTk

import logging
module_logger = logging.getLogger('friendly_gt.viewi.fgt_canvas')


class AutoScrollbar(ttk.Scrollbar):
    """
    Self hiding scrollbar.
    """

    def set(self, lo, hi):

        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
            ttk.Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise tk.TclError('Cannot use pack with the widget ' +
                          self.__class__.__name__)

    def place(self, **kw):
        raise tk.TclError('Cannot use place with the widget ' +
                          self.__class__.__name__)


class ScrollableImageCanvas:

    def __init__(self, placeholder, img, main_window, style):

        self._logger = logging.\
            getLogger('friendly_gt.view.ScrollableImageCanvas')

        self._style = style

        self.imscale = 1.0  # Scale of the image

        self._main_window = main_window

        self._delta = 1.3  # Zoom magnitude
        self._filter = Image.ANTIALIAS
        self._previous_state = 0  # The previous state of the keyboard
        self._imframe = ttk.Frame(placeholder)

        self.img = img

        # Scrollbars
        hbar = AutoScrollbar(self._imframe, orient='horizontal')
        vbar = AutoScrollbar(self._imframe, orient='vertical')

        hbar.grid(row=1, column=0, sticky='we')
        vbar.grid(row=0, column=1, sticky='ns')

        # Create the canvas
        self.canvas = tk.Canvas(self._imframe, highlightthickness=0,
                                xscrollcommand=hbar.set,
                                yscrollcommand=vbar.set)

        self.canvas.grid(row=0, column=0, sticky='nswe')

        background = self._style.lookup("Canvas.TFrame", 'background')

        self.canvas.config(background=background)
        self.canvas.update()  # Make sure the canvas updates

        self._orig_canvas_x = self.canvas.xview()[0]
        self._orig_canvas_y = self.canvas.yview()[0]

        hbar.configure(command=self._scroll_x)
        vbar.configure(command=self._scroll_y)

        # Bind events to the canvas
        # When the canvas is resized
        self.canvas.bind('<Configure>', lambda event: self._show_image())
        # Remember the canvas position
        self.canvas.bind('<ButtonPress-1>', self._move_from)

        # Move the canvas
        self.canvas.bind('<B1-Motion>', self._move_to)

        # Zoom for Windows and MacOs
        self.canvas.bind('<MouseWheel>', self._wheel)
        # Zoom for Linux, scroll down
        self.canvas.bind('<Button-5>', self._wheel)
        # Zoom for Linux, scroll up
        self.canvas.bind('<Button-4>', self._wheel)

        # Deal with keystrokes in idle mode
        self.canvas.bind('<Key>', lambda event:
                         self.canvas.after_idle(self._keystroke, event))

        # Decide if the image is too big
        self._huge = False
        self._huge_size = 14000
        self._band_width = 1024

        Image.MAX_IMAGE_PIXELS = 1000000000

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            self._image = Image.fromarray(self.img)

        self.imwidth, self.imheight = self._image.size

        if (self.imwidth * self.imheight > self._huge_size * self._huge_size
           and self._image.tile[0][0] == 'raw'):

            self._huge = True
            self._offset = self._image.tile[0][2]
            self._tile = [self._image.tile[0][0],
                          [0, 0, self.imwidth, 0],
                          self._offset,
                          self._image.tile[0][3]]

        self._min_side = min(self.imwidth, self.imheight)

        # Image Pyramid
        if self._huge:
            self._pyramid = [self.smaller()]
        else:
            self._pyramid = [Image.fromarray(self.img)]

        # Set ratio coefficeint for pyramid
        if self._huge:
            self._ratio = max(self.imwidth, self.imheight) / self._huge_size
        else:
            self._ratio = 1.0

        self._curr_img = 0  # The current image from the pyramid
        self._scale = self.imscale * self._ratio
        self._reduction = 2  # Reduction degree of pyramid

        w, h, = self._pyramid[-1].size
        while w > 512 and h > 512:
            w /= self._reduction
            h /= self._reduction
            self._pyramid.append(self._pyramid[-1].resize((int(w), int(h)),
                                 self._filter))

        # Put image into rectangle for setting corrdinates
        self.container = self.canvas.create_rectangle((0, 0, self.imwidth,
                                                      self.imheight), width=0)

        self._show_image()
        self.canvas.focus_set()

    def set_image(self, img):
        self.img = img
        self._show_image()
        self.canvas.focus_set()

    def set_theme(self, style):
        background = self._style.lookup("Canvas.TFrame", 'background')

        self.canvas.config(background=background)

    def smaller(self):
        """
        Resize the image to be smaller.


        Returns:
            A resized PIL image
        """
        w1, h1 = float(self.imwidth), float(self.imheight)
        w2, h2 = float(self._huge_size), float(self._huge_size)

        aspect_ratio1 = w1 / h1
        aspect_ratio2 = w2 / h2

        if aspect_ratio1 == aspect_ratio2:
            image = Image.new('RGB', (int(w2), int(h2)))
            k = h2 / h1  # Compression ratio
            w = int(w2)  # Band length
        elif aspect_ratio1 > aspect_ratio2:
            image = Image.new('RGB', (int(w2), int(w2 / aspect_ratio1)))
            k = h2 / w1
            w = int(w2)
        else:  # aspect_ratio1 < aspect_ratio2
            image = Image.new('RGB', (int(h2 * aspect_ratio1), int(h2)))
            k = h2 / h1
            w = int(h2 * aspect_ratio1)

        i, j, _ = 0, 1, round(0.5 + self.imheight / self._band_width)

        while i < self.imheight:
            # Width of the tile band
            band = min(self._band_width, self.imheight - i)

            self._tile[1][3] = band

            # Tile offset (3 bytes per pixel)
            self._tile[2] = self._offset + self.imwidth * i * 3
            self._image.close()
            self._image = Image.fromarray(self.img)
            self._image.size = (self.imwidth * band)
            self._image.tile = [self._tile]

            cropped = self._image.crop((0, 0, self.imwidth, band))  # crop
            image.paste(cropped.resize((w, int(band * k)+1), self._filer), (0,
                        int(i * k)))

            i += band
            j += 1

        return image

    def redraw_figures(self):
        """
        Dummy function for redrawing in children classes


        Returns:
            None
        """
        pass

    def grid(self, **kw):
        """
        Put the Canvas widget on the parent widget.

        Args:
            **kw: Kwargs

        Returns:
            None
        """
        self._imframe.grid(**kw)  # Put the canvas on the grid
        self._imframe.grid(sticky='nswe')  # Make frame sticky
        self._imframe.rowconfigure(0, weight=1)  # Make canvas expandable
        self._imframe.columnconfigure(0, weight=1)

    def pack(self, **kw):
        """
        Cannot use pack.

        Args:
            **kw: Kwargs

        Returns:
            None

        Raises:
            Exception, you can't use the pack function.
        """
        raise Exception('Cannot use pack with the widget ' +
                        self._class_._name_)

    def place(self, **kw):
        """
        The place method of the tkinter widget.

        Args:
            **kw: kwargs

        Returns:
            None

        Raises:
            An exception, as this cannot be used with this widget.
        """
        raise Exception('Cannot use place with the widget ' +
                        self._class_._name_)

    # noinspection PyUnusedLocal
    def _scroll_x(self, *args, **kwargs):
        """
        Scroll in the x direction.

        Args:
            *args: args
            **kwargs: kwargs

        Returns:
            None

        Postconditions:
            The canvas is scrolled horizontally.
        """
        self.canvas.xview(*args)  # scroll horizontally
        self._show_image()  # redraw the image

    # noinspection PyUnusedLocal
    def _scroll_y(self, *args, **kwargs):
        """
        Scroll in the y direction

        Args:
            *args: args
            **kwargs: kwargs

        Returns:
            None

        Postconditions:
            The canvas is scrolled vertically.
        """
        self.canvas.yview(*args)  # scroll vertically
        self._show_image()  # redraw the image

    def _show_image(self):
        """
        Display the current image


        Returns:
            None

        Postconditions:
            The image is drawn on the canvas.
        """
        box_image = self.canvas.coords(self.container)  # get image area
        box_canvas = (self.canvas.canvasx(0),  # get visible area of the canvas
                      self.canvas.canvasy(0),
                      self.canvas.canvasx(self.canvas.winfo_width()),
                      self.canvas.canvasy(self.canvas.winfo_height()))

        # convert to integer or it will not work properly
        box_img_int = tuple(map(int, box_image))  # Get scroll region box

        box_img_width = box_img_int[2] - box_img_int[0]

        xscale = box_img_width/self.img.shape[1]

        self._coord_scale = xscale

        box_scroll = [min(box_img_int[0], box_canvas[0]),
                      min(box_img_int[1], box_canvas[1]),
                      max(box_img_int[2], box_canvas[2]),
                      max(box_img_int[3], box_canvas[3])]

        # Horizontal part of the image is in the visible area
        if box_scroll[0] == box_canvas[0] and box_scroll[2] == box_canvas[2]:
            box_scroll[0] = box_img_int[0]
            box_scroll[2] = box_img_int[2]
        # Vertical part of the image is in the visible area
        if box_scroll[1] == box_canvas[1] and box_scroll[3] == box_canvas[3]:
            box_scroll[1] = box_img_int[1]
            box_scroll[3] = box_img_int[3]
        # Convert scroll region to tuple and to integer
        # set scroll region
        self.canvas.configure(scrollregion=tuple(map(int, box_scroll)))

        # get coordinates (x1,y1,x2,y2) of the image tile
        x1 = max(box_canvas[0] - box_image[0], 0)
        y1 = max(box_canvas[1] - box_image[1], 0)
        x2 = min(box_canvas[2], box_image[2]) - box_image[0]
        y2 = min(box_canvas[3], box_image[3]) - box_image[1]

        # show image if it in the visible area
        if int(x2 - x1) > 0 and int(y2 - y1) > 0:
            if self._huge and self._curr_img < 0:  # show huge image
                h = int((y2 - y1) / self.imscale)  # height of the tile band
                self._tile[1][3] = h  # set the tile band height
                self._tile[2] = (self._offset + self.imwidth *
                                 int(y1 / self.imscale) * 3)
                self._image.close()
                self._image = Image.open(self.path)  # reopen / reset image
                # set size of the tile band
                self._image.size = (self.imwidth, h)
                self._image.tile = [self._tile]
                image = self._image.crop((int(x1 / self.imscale), 0,
                                          int(x2 / self.imscale), h))
            else:  # show normal image
                # crop current img from pyramid
                image = self._pyramid[max(0, self._curr_img)].crop(
                                    (int(x1 / self._scale),
                                     int(y1 / self._scale),
                                     int(x2 / self._scale),
                                     int(y2 / self._scale)))
            #
            imagetk = ImageTk.PhotoImage(image.resize((int(x2 - x1),
                                         int(y2 - y1)), self._filter))

            imageid = self.canvas.create_image(max(box_canvas[0],
                                               box_img_int[0]),
                                               max(box_canvas[1],
                                               box_img_int[1]),
                                               anchor='nw', image=imagetk)
            self.canvas.lower(imageid)  # set image into background
            # keep an extra reference to prevent garbage-collection
            self.canvas.imagetk = imagetk
            self._image_id = imageid

    def _move_from(self, event):
        """
        Mark the position of the canvas to move from using scanning.

        Args:
            event: The mouse event

        Returns:
            None

        Postconditions:
            The canvas will have a scan mark at the event position.
        """
        self.canvas.scan_mark(event.x, event.y)

    def _move_to(self, event):
        """
        Move the canvas to the event position.

        Args:
            event: The mouse event.

        Returns:
            None

        Postconditions:
            The canvas is moved to the event position.
        """
        self.canvas.scan_dragto(event.x, event.y, gain=1)

        self._show_image()  # zoom tile and show it on the canvas

    def outside(self, x, y):
        """
        Check it the input point is inside the image area.

        Args:
            x: The x coordinate
            y: The y coordinate

        Returns:
            True if the point is inside the image.
            False if the point is outside the image.
        """
        bbox = self.canvas.coords(self.container)  # get image area
        if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]:
            return False  # point (x,y) is inside the image area
        else:
            return True  # point (x,y) is outside the image area

    def set_zoom(self, factor):
        x, y = 0, 0
        scale = 1.0
        if factor < 0:
            if round(self._min_side * self.imscale) < 30:
                return  # image is less than 30 pixels
            self.imscale /= (self._delta * (-factor))
            scale /= (self._delta * (-factor))

        if factor > 0:
            i = min(self.canvas.winfo_width(), self.canvas.winfo_height()) >> 1
            if i < self.imscale:
                return  # 1 pixel is bigger than the visible area
            self.imscale *= self._delta
            scale *= self._delta

        # Take appropriate image from the pyramid
        k = self.imscale * self._ratio  # temporary coefficient
        self._curr_img = min((-1) * int(math.log(k, self._reduction)),
                             len(self._pyramid) - 1)
        self._scale = k * math.pow(self._reduction, max(0, self._curr_img))
        #
        self.canvas.scale('all', x, y, scale, scale)  # rescale all objects
        # Redraw some figures before showing image on the screen
        self.redraw_figures()  # method for child classes
        self._show_image()

    def _wheel(self, event):
        """
        Called when the mouse wheel is scrolled.

        Args:
            event: The mouse event.

        Returns:
            None

        Postconditions:
            The image on the canvas is zoomed.
        """
        # get coordinates of the event on the canvas
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        if self.outside(x, y):
            return  # zoom only inside image area

        # Don't scroll if control is down
        if event.state - self._previous_state == 4:
            return

        scale = 1.0
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta == -120:  # scroll down, smaller
            if round(self._min_side * self.imscale) < 30:
                return  # image is less than 30 pixels
            self.imscale /= self._delta
            scale /= self._delta
        if event.num == 4 or event.delta == 120:  # scroll up, bigger
            i = min(self.canvas.winfo_width(), self.canvas.winfo_height()) >> 1
            if i < self.imscale:
                return  # 1 pixel is bigger than the visible area
            self.imscale *= self._delta
            scale *= self._delta
        # Take appropriate image from the pyramid
        k = self.imscale * self._ratio  # temporary coefficient
        self._curr_img = min((-1) * int(math.log(k, self._reduction)),
                             len(self._pyramid) - 1)
        self._scale = k * math.pow(self._reduction, max(0, self._curr_img))
        #
        self.canvas.scale('all', x, y, scale, scale)  # rescale all objects
        # Redraw some figures before showing image on the screen
        self.redraw_figures()  # method for child classes
        self._show_image()

    def _keystroke(self, event):
        """
        Called when the keybord is used.

        Args:
            event: The keyboard event.

        Returns:
            None

        Postconditions:
            The canvas is modified according to the key pressed.
        """
        # means that the Control key is pressed
        if event.state - self._previous_state == 4:
            pass  # do nothing if Control key is pressed
        else:
            # remember the last keystroke state
            self._previous_state = event.state

    def crop(self, bbox):
        """
        Crop the image using the given bounding box.

        Args:
            bbox: The bounding box, a list

        Returns:
            The cropped image.
        """
        if self._huge:  # image is huge and not totally in RAM
            band = bbox[3] - bbox[1]  # width of the tile band
            self._tile[1][3] = band  # set the tile height
            # set offset of the band
            self._tile[2] = self._offset + self.imwidth * bbox[1] * 3
            self._image.close()
            self._image = Image.open(self.path)  # reopen / reset image
            # set size of the tile band
            self._image.size = (self.imwidth, band)
            self._image.tile = [self._tile]
            return self._image.crop((bbox[0], 0, bbox[2], band))
        else:  # image is totally in RAM
            return self._pyramid[0].crop(bbox)

    def destroy(self):
        """ ImageFrame destructor """
        self._image.close()
        map(lambda i: i.close, self._pyramid)  # close all pyramid images
        del self._pyramid[:]  # delete pyramid list
        del self._pyramid  # delete pyramid variable
        self.canvas.destroy()
        self._imframe.destroy()


class PatchNavCanvas(ScrollableImageCanvas):

    def __init__(self, placeholder, img, main_window, style):

        self._logger = logging.getLogger('friendly_gt.view.FGTCanvas')

        super(PatchNavCanvas, self).__init__(placeholder, img, main_window,
                                             style)

        borderwidth = self._style.lookup("Preview.TFrame", 'borderwidth')

        relief = self._style.lookup("Preview.TFrame", 'relief')

        self.canvas.config(borderwidth=borderwidth, relief=relief)

        self.canvas.bind("<ButtonRelease-1>", self._on_click_release)

        self._dragged = False
        self._roi = False
        self._select_id = None

    def _on_click_release(self, event):
        """
        Called when the left mouse button is released.

        Args:
            event: The mouse event.

        Returns:
            None
        """

        if self._roi:
            self._roi = False
            self.canvas.delete(self._select_id)
            self._select_id = None

            start = self._convert_canvas_coord_to_image(self._select_x,
                                                        self._select_y)

            end = self._convert_canvas_coord_to_image(self._select_end_x,
                                                      self._select_end_y)

            self._main_window.stop_roi(start, end)

            self.canvas.config(cursor="arrow")
            return

        if self._dragged:
            self._dragged = False
            return

        pos = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)

        container_coords = self.canvas.coords(self.container)
        pos = pos[0] - container_coords[0], pos[1] - container_coords[1]

        pos = pos[0] / self._coord_scale, pos[1] / self._coord_scale

        self._main_window.navigate_to_patch(pos)

    def _convert_canvas_coord_to_image(self, x, y):

        container_coords = self.canvas.coords(self.container)
        pos = x - container_coords[0], y - container_coords[1]

        pos = pos[0] / self._coord_scale, pos[1] / self._coord_scale

        return pos

    def set_image(self, image):

        self.img = image
        self._image = Image.fromarray(image)

        pyramid_index = max(0, self._curr_img)

        old_img = self._pyramid[pyramid_index]

        new_image = self._image.resize(old_img.size, self._filter)

        self._pyramid[pyramid_index] = new_image

        self._show_image()

        t = threading.Thread(target=self.recompute_pyramid, name="pyramid")
        t.daemon = True
        t.start()

    def new_image(self, image, patch_offset=(0, 0)):
        """
        Reset the image and all properties of the image on the canvas.

        Args:
            image: The image, a numpy array.
            patch_offset: The offset of the current patch within the image

        Returns:
            None
        """
        self.imscale = 1.0

        self.canvas.delete("all")
        self.img = image

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            self._image = Image.fromarray(self.img)

        self.imwidth, self.imheight = self._image.size

        if (self.imwidth * self.imheight > self._huge_size * self._huge_size
           and self._image.tile[0][0] == 'raw'):

            self._huge = True
            self._offset = self._image.tile[0][2]
            self._tile = [self._image.tile[0][0],
                          [0, 0, self.imwidth, 0],
                          self._offset,
                          self._image.tile[0][3]]

        self._min_side = min(self.imwidth, self.imheight)

        # Image Pyramid
        if self._huge:
            self._pyramid = [self.smaller()]
        else:
            self._pyramid = [Image.fromarray(self.img)]

        # Set ratio coefficeint for pyramid
        if self._huge:
            self._ratio = max(self.imwidth, self.imheight) / self._huge_size
        else:
            self._ratio = 1.0

        self._curr_img = 0  # The current image from the pyramid
        self._scale = self.imscale * self._ratio
        self._reduction = 2  # Reduction degree of pyramid

        w, h, = self._pyramid[-1].size
        while w > 512 and h > 512:
            w /= self._reduction
            h /= self._reduction
            self._pyramid.append(self._pyramid[-1].resize((int(w), int(h)),
                                 self._filter))

        # Put image into rectangle for setting corrdinates
        self.container = self.canvas.create_rectangle((0, 0, self.imwidth,
                                                      self.imheight), width=0)

        self._show_image()

    def recompute_pyramid(self):

        new_pyramid = []
        for img in self._pyramid:
            new_image = self._image.resize(img.size, self._filter)
            new_pyramid.append(new_image)

        self._pyramid = new_pyramid

    def _move_to(self, event):
        """
        Move the canvas to the event position.

        Args:
            event: The mouse event.

        Returns:
            None

        Postconditions:
            The canvas is moved to the event position.
        """
        if self._roi:
            if self._select_id is None:
                self._create_selection_rect(event)
            else:
                self._update_selection_rect(event)

        else:

            self._dragged = True

            super()._move_to(event)

    def _update_selection_rect(self, event):

        pos = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)

        self.canvas.coords(self._select_id, self._select_x, self._select_y,
                           pos[0], pos[1])

        self._select_end_x = pos[0]
        self._select_end_y = pos[1]

    def _create_selection_rect(self, event):

        pos = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)

        self._select_id = self.canvas.create_rectangle(pos[0], pos[1],
                                                       pos[0], pos[1],
                                                       dash=(2, 2), fill='',
                                                       outline='white')

        self._select_x = pos[0]
        self._select_y = pos[1]

    def activate_roi(self):
        self._roi = True
        self.canvas.config(cursor="cross")


class FGTCanvas(ScrollableImageCanvas):
    """
    A canvas that allows panning and zooming of large images.

    Attributes:
        imscale: The current scale of the image
        cursor: The current cursor to use on the image
    """

    def __init__(self, placeholder, img, main_window, style):

        self._logger = logging.getLogger('friendly_gt.view.FGTCanvas')

        super(FGTCanvas, self).__init__(placeholder, img, main_window, style)

        self._previous_position = (0, 0)
        self._coord_scale = 1
        self._dragged = False
        self._prev_offset = (0, 0)
        self._drag_id = ''
        self._unique_drag_id = 0

        # Bind events to the canvas
        self.canvas.bind('<ButtonRelease-1>', self._on_click_release)

        # Move the canvas
        self.canvas.bind('<B2-Motion>', self._right_drag)
        self.canvas.bind('<ButtonPress-2>', self._right_click)
        self.canvas.bind('<B3-Motion>', self._right_drag)
        self.canvas.bind('<ButtonPress-3>', self._right_click)

        # Cursor stuff
        self.canvas.bind('<Motion>', self._on_motion)
        self.canvas.bind('<Enter>', self._set_cursor)
        self.canvas.bind('<Leave>', self._default_cursor)
        self.canvas.bind('<FocusOut>', self._default_cursor)
        self.canvas.bind('<FocusIn>', self._set_cursor)

        self._cursor = "arrow"
        self._brush_cursor = None
        self._brush_radius = None

    @property
    def cursor(self):
        return self._cursor

    @cursor.setter
    def cursor(self, value):
        self._cursor = value
        self._set_cursor(None)

    @property
    def brush_radius(self):
        return self._brush_radius

    @brush_radius.setter
    def brush_radius(self, value):
        self._brush_radius = value
        self.draw_brush()

    def new_image(self, image, patch_offset=(0, 0)):
        """
        Reset the image and all properties of the image on the canvas.

        Args:
            image: The image, a numpy array.
            patch_offset: The offset of the current patch within the image

        Returns:
            None
        """
        self.imscale = 1.0

        self.canvas.delete("all")
        self.img = image

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            self._image = Image.fromarray(self.img)

        self.imwidth, self.imheight = self._image.size

        if (self.imwidth * self.imheight > self._huge_size * self._huge_size
           and self._image.tile[0][0] == 'raw'):

            self._huge = True
            self._offset = self._image.tile[0][2]
            self._tile = [self._image.tile[0][0],
                          [0, 0, self.imwidth, 0],
                          self._offset,
                          self._image.tile[0][3]]

        self._min_side = min(self.imwidth, self.imheight)

        # Image Pyramid
        if self._huge:
            self._pyramid = [self.smaller()]
        else:
            self._pyramid = [Image.fromarray(self.img)]

        # Set ratio coefficeint for pyramid
        if self._huge:
            self._ratio = max(self.imwidth, self.imheight) / self._huge_size
        else:
            self._ratio = 1.0

        self._curr_img = 0  # The current image from the pyramid
        self._scale = self.imscale * self._ratio
        self._reduction = 2  # Reduction degree of pyramid

        w, h, = self._pyramid[-1].size
        while w > 512 and h > 512:
            w /= self._reduction
            h /= self._reduction
            self._pyramid.append(self._pyramid[-1].resize((int(w), int(h)),
                                 self._filter))

        # Put image into rectangle for setting corrdinates
        self.container = self.canvas.create_rectangle((0, 0, self.imwidth,
                                                      self.imheight), width=0)

        self._show_image()

        # Deal with 0 offsets in the y coordinate
        if patch_offset[1] == 0 and patch_offset[0] != 0:
            patch_offset = patch_offset[0], self._prev_offset[1]

        self._prev_offset = patch_offset

        # The anchor point will be moved to (0, 0) in the window
        # We want to account for the patch offset, but not put the current
        # patch right in the corner
        anchorx = -self.canvas.canvasx(0 - (patch_offset[1]/2))
        anchory = -self.canvas.canvasy(0 - (patch_offset[0]/2))

        self.canvas.scan_mark(int(anchorx), int(anchory))
        self.canvas.scan_dragto(0, 0, gain=1)
        self.canvas.focus_set()

        self._show_image()

    def _on_motion(self, event):
        """
        Called when the mouse is moved.

        Args:
            event: The mouse event.

        Returns:
            None

        Postconditions:
            The mouse cursor is drawn.
            Previous position is set.
        """
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        pos = (x, y)

        if self._cursor == "brush":
            self.draw_brush(pos)

        self._previous_position = pos

    def _set_cursor(self, event):
        """
        Set the cursor to the current specified icon.

        Args:
            event: Event

        Returns:
            None
        """
        if self._cursor == "brush":
            self.canvas.config(cursor="none")
            self.draw_brush()
        else:
            self.canvas.config(cursor=self._cursor)
            if self._brush_cursor is not None:
                self.canvas.delete(self._brush_cursor)

    def _default_cursor(self, event):
        """
        Set the cursor back to the default.

        Args:
            event: The event

        Returns:
            None
        """
        self.canvas.config(cursor="arrow")
        self._previous_position = (50, 50)

    def draw_brush(self, pos=None):
        """
        Draw the paintbrush cursor

        Args:
            pos: The position to draw the brush at.  The default value is None.

        Returns:
            None

        Postcondition:
            The brush is drawn on the canvas/
        """
        if self._brush_cursor is not None:
            self.canvas.delete(self._brush_cursor)

        if self._brush_radius is None:
            self._brush_radius = 15

        if pos is None:
            pos = self._previous_position

        x_max = pos[0] + (self._brush_radius * self._coord_scale)
        x_min = pos[0] - (self._brush_radius * self._coord_scale)
        y_max = pos[1] + (self._brush_radius * self._coord_scale)
        y_min = pos[1] - (self._brush_radius * self._coord_scale)

        self._brush_cursor = self.canvas.create_oval(x_max, y_max, x_min,
                                                     y_min,
                                                     outline='white',
                                                     tag='brush')

    def _move_from(self, event):
        """
        Mark the position of the canvas to move from using scanning.

        Args:
            event: The mouse event

        Returns:
            None

        Postconditions:
            The canvas will have a scan mark at the event position.
        """
        if self._cursor != "brush":
            self.canvas.scan_mark(event.x, event.y)

    def _right_click(self, event):
        """
        For dragging with right mouse button.

        Args:
            event: The mouse event.

        Returns:
            None
        """
        self.canvas.scan_mark(event.x, event.y)

    def _on_click_release(self, event):
        """
        Called when the left mouse button is released.

        Args:
            event: The mouse event.

        Returns:
            None
        """

        if self._dragged:
            self._dragged = False
            return

        pos = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)

        container_coords = self.canvas.coords(self.container)
        pos = pos[0] - container_coords[0], pos[1] - container_coords[1]

        pos = pos[0] / self._coord_scale, pos[1] / self._coord_scale
        self._main_window.on_canvas_click(pos)

    def _move_to(self, event):
        """
        Move the canvas to the event position.

        Args:
            event: The mouse event.

        Returns:
            None

        Postconditions:
            The canvas is moved to the event position.
        """
        self._dragged = True
        if self._cursor != "brush":

            self.canvas.scan_dragto(event.x, event.y, gain=1)

        if self._cursor == "brush":

            if self._drag_id == '':
                self._logger.debug("Drag start")
            else:
                self._main_window._master.after_cancel(self._drag_id)

            self._drag_id = self._main_window._master.\
                after(300, self._stop_dragging)

            pos = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
            self._previous_position = pos
            container_coords = self.canvas.coords(self.container)
            pos = pos[0] - container_coords[0], pos[1] - container_coords[1]
            pos = pos[0] / self._coord_scale, pos[1] / self._coord_scale

            self._main_window.on_canvas_drag(pos, drag_id=self._unique_drag_id)

            brush_pos = (self.canvas.canvasx(event.x),
                         self.canvas.canvasy(event.y))

            self.draw_brush(brush_pos)

        self._show_image()  # zoom tile and show it on the canvas

    def _stop_dragging(self):
        self._drag_id = ''
        self._unique_drag_id += 1

    def _right_drag(self, event):
        """
        Drag with the right mouse button.

        Args:
            event: The mouse event.

        Returns:
            None
        """
        self.canvas.scan_dragto(event.x, event.y, gain=1)

        self._show_image()
