"""
File Name: test_view.py

Authors: Kyle Seidenthal

Date: 12-03-2020

Description: Test cases for the view

"""
import pytest

from mock import MagicMock  # , PropertyMock

from friendly_ground_truth.view.tk_view import (MainWindow, AboutDialog,
                                                KeyboardShortcutDialog)


class TestView():
    """
    Test cases for the View
    """

    @pytest.fixture
    def setup(self, mocker):
        self.mock_controller = mocker.patch('friendly_ground_truth.' +
                                            'controller.controller.Controller')

        mocker.patch("tkinter.Tk")

    def test_set_up_interactions_other(self, setup, mocker):
        """
        Test setting up interactions on som other platforms

        :test condition: bind_all is called

        :param setup: The setup fixture
        :param mocker: Mocker
        :returns: None
        """

        from friendly_ground_truth.view import tk_view

        tk_view.platform = ''

        window = MainWindow(self.mock_controller, MagicMock())

        patch_bind = mocker.patch.object(window, 'bind_all')

        window.set_up_interactions()

        patch_bind.assert_called()

    def test_set_up_interactions_linux(self, setup, mocker):
        """
        Test setting up interactions on linux

        :test condition: bind_all is called with <Button-4> and <Button-5>

        :param setup: The setup fixture
        :param mocker: Mocker
        :returns: None
        """

        from friendly_ground_truth.view import tk_view

        tk_view.platform = 'linux'

        window = MainWindow(self.mock_controller, MagicMock())

        patch_bind = mocker.patch.object(window, 'bind_all')

        window.set_up_interactions()

        patch_bind.assert_called()

    def test_set_up_interactions_darwin(self, setup, mocker):
        """
        Test setting up interactions on mac

        :test condition: bind_all is called with <Mousewheel>

        :param setup: The setup fixture
        :param mocker: Mocker
        :returns: None
        """

        from friendly_ground_truth.view import tk_view

        tk_view.platform = 'darwin'

        window = MainWindow(self.mock_controller, MagicMock())

        patch_bind = mocker.patch.object(window, 'bind_all')

        window.set_up_interactions()

        patch_bind.assert_called()

    def test_set_up_interactions_windows(self, setup, mocker):
        """
        Test setting up interactions on windows

        :test condition: bind_all is called with <Mousewheel>

        :param setup: The setup fixture
        :param mocker: Mocker
        :returns: None
        """

        from friendly_ground_truth.view import tk_view

        tk_view.platform = 'win32'

        window = MainWindow(self.mock_controller, MagicMock())

        patch_bind = mocker.patch.object(window, 'bind_all')

        window.set_up_interactions()

        patch_bind.assert_called()

    def test_create_canvas(self, setup, mocker):
        """
        Test creation of canvas

        :test_condition: tk.Canvas is called

        :param setup: Setup fixture
        :param mocker: Mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())

        tk_patch = mocker.patch('tkinter.Canvas')

        window.create_canvas()

        tk_patch.assert_called()

    def test_create_menubar(self, setup, mocker):
        """
        Test creation of menubar

        :test_condition: tk.Menu is called

        :param setup: Setup fixture
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())

        tk_patch = mocker.patch('tkinter.Menu')

        window.create_menubar()

        tk_patch.assert_called()

    def test_create_file_menu(self, setup, mocker):
        """
        Test creating the file menu

        :test_condition: tk.Menu is called

        :param setup: setup fixture
        :param mocker: mocker
        :returns: None
        """
        window = MainWindow(self.mock_controller, MagicMock())

        tk_patch = mocker.patch('tkinter.Menu')

        window.create_file_menu()

        tk_patch.assert_called()

    def test_create_toolbar(self, setup, mocker):
        """
        Test creating the toolbar

        :test_condition: tk.Frame is called

        :param setup: Setup fixture
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())

        tk_patch = mocker.patch('tkinter.Frame')

        window.create_toolbar()

        tk_patch.assert_called()

    def test_on_left(self, setup, mocker):
        """
        Test when the left key is pressed

        :test_condition: on_prev_tool() is called

        :param setup: setup fixture
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())

        event = MagicMock()

        spy = mocker.spy(window, 'on_prev_tool')

        window.on_left(event)

        spy.assert_called()

    def test_on_right(self, setup, mocker):
        """
        Test when the right key is pressed

        :test_condition: on_next_tool() is called

        :param setup: Setup fixture
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())

        event = MagicMock()

        spy = mocker.spy(window, 'on_next_tool')

        window.on_right(event)

        spy.assert_called()

    def test_on_keypress_x(self, setup, mocker):
        """
        Test when the x key is pressed

        :test_condition: on_no_root_tool() is called

        :param setup: Setup fixture
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())

        event = MagicMock()
        event.char = 'x'

        spy = mocker.spy(window, 'on_no_root_tool')

        window.on_keypress(event)

        spy.assert_called()

    def test_on_keypress_t(self, setup, mocker):
        """
        Test when the t key is pressed

        :test_condition: on_threshold_tool() is called

        :param setup: Setup fixture
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())

        event = MagicMock()
        event.char = 't'

        spy = mocker.spy(window, 'on_threshold_tool')

        window.on_keypress(event)

        spy.assert_called()

    def test_on_keypress_z(self, setup, mocker):
        """
        Test when the z key is pressed

        :test_condition: on_zoom_tool() is called

        :param setup: Setup fixture
        :param mocker: mocker
        :returns: None
        """
        window = MainWindow(self.mock_controller, MagicMock())

        event = MagicMock()
        event.char = 'z'

        spy = mocker.spy(window, 'on_zoom_tool')

        window.on_keypress(event)

        spy.assert_called()

    def test_on_keypress_a(self, setup, mocker):
        """
        Test when the a key is pressed

        :test_condition: on_add_reg_tool() is called

        :param setup: Setup fixture
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())

        event = MagicMock()
        event.char = 'a'

        spy = mocker.spy(window, 'on_add_reg_tool')

        window.on_keypress(event)

        spy.assert_called()

    def test_on_keypress_r(self, setup, mocker):
        """
        Test when the r key is pressed

        :test_condition: on_remove_reg_tool() is called

        :param setup: Setup fixture
        :param mocker: mocker
        :returns: None
        """
        window = MainWindow(self.mock_controller, MagicMock())

        event = MagicMock()
        event.char = 'r'

        spy = mocker.spy(window, 'on_remove_reg_tool')

        window.on_keypress(event)

        spy.assert_called()

    def test_on_keypress_f(self, setup, mocker):
        """
        Test when the f key is pressed

        :test_condition: on_flood_add_tool() is called

        :param setup: Setup fixture
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())

        event = MagicMock()
        event.char = 'f'

        spy = mocker.spy(window, 'on_flood_add_tool')

        window.on_keypress(event)

        spy.assert_called()

    def test_on_keypress_l(self, setup, mocker):
        """
        Test when the l key is pressed

        :test_condition: on_flood_remove_tool() is called

        :param setup: Setup fixture
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())

        event = MagicMock()
        event.char = 'l'

        spy = mocker.spy(window, 'on_flood_remove_tool')

        window.on_keypress(event)

        spy.assert_called()

    def test_on_keypress_c(self, setup, mocker):
        """
        Test when the c key is pressed

        :test_condition: on_add_cross_tool() is called

        :param setup: Setup fixture
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())

        event = MagicMock()
        event.char = 'c'

        spy = mocker.spy(window, 'on_add_cross_tool')

        window.on_keypress(event)

        spy.assert_called()

    def test_on_keypress_v(self, setup, mocker):
        """
        Test when the v key is pressed

        :test_condition: on_add_tip_tool() is called

        :param setup: Setup fixture
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())

        event = MagicMock()
        event.char = 'v'

        spy = mocker.spy(window, 'on_add_tip_tool')

        window.on_keypress(event)

        spy.assert_called()

    def test_on_keypress_b(self, setup, mocker):
        """
        Test when the b key is pressed

        :test_condition: on_add_branch_tool() is called

        :param setup: Setup fixture
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())

        event = MagicMock()
        event.char = 'b'

        spy = mocker.spy(window, 'on_add_branch_tool')

        window.on_keypress(event)

        spy.assert_called()

    def test_on_keypress_n(self, setup, mocker):
        """
        Test when the n key is pressed

        :test_condition: on_remove_landmark_tool() is called

        :param setup: Setup fixture
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())

        event = MagicMock()
        event.char = 'n'

        spy = mocker.spy(window, 'on_remove_landmark_tool')

        window.on_keypress(event)

        spy.assert_called()

    def test_on_keypress_invalid(self, setup, mocker):
        """
        Test when an invalid key is pressed

        :test_condition: returns none

        :param setup: Setup fixture
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())

        event = MagicMock()
        event.char = 'w'

        result = window.on_keypress(event)
        assert result is None

    def test_on_load_image(self, setup, mocker):
        """
        Test the load image button

        :test_condition: controller.load_new_image() called

        :param setup: setup
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())

        window.on_load_image()

        self.mock_controller.load_new_image.assert_called()

    def test_show_image_no_id(self, setup, mocker):
        """
        Test the show image function when no image id exists

        :test_condition: canvas.delete() is not called

        :param setup: setup
        :param mocker: mocker
        :returns: None
        """
        mock_image = MagicMock()
        mock_image.size = (5, 5)
        mocker.patch('PIL.Image.fromarray', return_value=mock_image)
        mocker.patch('PIL.ImageTk.PhotoImage')

        window = MainWindow(self.mock_controller, MagicMock())

        window.image_id = None
        window.canvas = MagicMock()

        img = MagicMock()
        img.size = (5, 5)

        window.show_image(img)

        window.canvas.delete.assert_not_called()

    def test_show_image_id(self, setup, mocker):
        """
        Test the show image function when an image id exists

        :test_condition: canvas.delete() is called

        :param setup: setup
        :param mocker: mocker
        :returns: None
        """

        mock_image = MagicMock()
        mock_image.size = (5, 5)
        mocker.patch('PIL.Image.fromarray', return_value=mock_image)
        mocker.patch('PIL.ImageTk.PhotoImage')

        window = MainWindow(self.mock_controller, MagicMock())

        window.image_id = 5
        window.canvas = MagicMock()

        img = MagicMock()
        img.size = (5, 5)

        window.show_image(img)

        window.canvas.delete.assert_called()

    def test_on_save_mask(self, setup, mocker):
        """
        Test when the save mask button is pressed

        :test_Condition: controller.save_mask() is called

        :param setup: setup
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())

        window.on_save_mask()

    def test_on_about(self, setup, mocker):
        """
        Test when the about button is pressed

        :test_Condition: A dialog box is created

        :param setup: setup
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())

        mock_dialog = mocker.patch("friendly_ground_truth.view."
                                   "tk_view.AboutDialog")

        window.on_about()

        mock_dialog.assert_called()

    def test_on_keyboard_shortcut(self, setup, mocker):
        """
        Test when the keyboard shortcuts button is pressed

        :test_Condition: A dialog box is created

        :param setup: setup
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())

        mock_dialog = mocker.patch("friendly_ground_truth.view."
                                   "tk_view.KeyboardShortcutDialog")

        window.on_keyboard_shortcuts()

        mock_dialog.assert_called()

    def test_change_toolbar_state(self, setup, mocker):
        """
        Test changing the toolbar state

        :test_condition: button.config is called

        :param setup: setup
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())

        window.toolbar_buttons = {window.ID_TOOL_THRESH: MagicMock(), 7:
                                  MagicMock()}

        window.change_toolbar_state(window.ID_TOOL_THRESH)
        window.toolbar_buttons[window.ID_TOOL_THRESH]\
            .config.assert_called_once()

    def test_on_threshold_tool(self, setup, mocker):
        """
        Test when the threshold tool is chosen

        :test_condition: controller.change_mode is called with ID_TOOL_THRESH

        :param setup: setup
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())
        window.on_threshold_tool()

        self.mock_controller.change_mode\
                            .assert_called_with(window.ID_TOOL_THRESH)

    def test_on_add_reg_tool(self, setup, mocker):
        """
        Test when the add region tool is chosen

        :test_condition: controller.change_mode is called with ID_TOOL_ADD

        :param setup: setup
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())
        window.on_add_reg_tool()

        self.mock_controller.change_mode\
                            .assert_called_with(window.ID_TOOL_ADD)

    def test_on_remove_reg_tool(self, setup, mocker):
        """
        Test when the remove region tool is chosen

        :test_condition: controller.change_mode is called with ID_TOOL_REMOVE

        :param setup: setup
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())
        window.on_remove_reg_tool()

        self.mock_controller.change_mode\
                            .assert_called_with(window.ID_TOOL_REMOVE)

    def test_on_no_root_tool(self, setup, mocker):
        """
        Test when the no root tool is chosen

        :test_condition: controller.change_mode is called with ID_TOOL_NO_ROOT

        :param setup: setup
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())
        window.on_no_root_tool()

        self.mock_controller.change_mode\
                            .assert_called_with(window.ID_TOOL_NO_ROOT)

    def test_on_zoom_tool(self, setup, mocker):
        """
        Test when the zoom tool is chosen

        :test_condition: controller.change_mode is called with ID_TOOL_ZOOM

        :param setup: setup
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())
        window.on_zoom_tool()

        self.mock_controller.change_mode\
                            .assert_called_with(window.ID_TOOL_ZOOM)

    def test_on_flood_add_tool(self, setup, mocker):
        """
        Test when the flood add region tool is chosen

        :test_condition: controller.change_mode is called with
                         ID_TOOL_FLOOD_ADD

        :param setup: setup
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())
        window.on_flood_add_tool()

        self.mock_controller.change_mode\
                            .assert_called_with(window.ID_TOOL_FLOOD_ADD)

    def test_on_flood_remove_tool(self, setup, mocker):
        """
        Test when the flood remove region tool is chosen

        :test_condition: controller.change_mode is called with
                         ID_TOOL_FLOOD_REMOVE

        :param setup: setup
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())
        window.on_flood_remove_tool()

        self.mock_controller.change_mode\
                            .assert_called_with(window.ID_TOOL_FLOOD_REMOVE)

    def test_on_prev_tool(self, setup, mocker):
        """
        Test when the prev tool is chosen

        :test_condition: controller.prev_patch() is called

        :param setup: setup
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())
        window.on_prev_tool()

        self.mock_controller.prev_patch.assert_called()

    def test_on_next_tool(self, setup, mocker):
        """
        Test when the next tool is chosen

        :test_condition: controller.next_patch()

        :param setup: setup
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())
        window.on_next_tool()

        self.mock_controller.next_patch.assert_called()

    def test_on_mousewheel_4(self, setup, mocker):
        """
        Test when the mousewheel is used and event.num is 4 and event.delta is
        0

        :test_condition: controller.handle_mouse_wheel is called with 120

        :param setup: setup
        :param mocker: mocker
        :returns: None
        """
        window = MainWindow(self.mock_controller, MagicMock())

        event = MagicMock()
        event.num = 4
        event.delta = 0

        window.on_mousewheel(event)

        self.mock_controller.handle_mouse_wheel.assert_called_with(120)

    def test_on_mousewheel_5(self, setup, mocker):
        """
        Test when the mousewheel is used and event.num is 5 and event.delta is
        0
        :test_condition: controller.handle_mouse_wheel is called with -120

        :param setup: setup
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())

        event = MagicMock()
        event.num = 5
        event.delta = 0

        window.on_mousewheel(event)

        self.mock_controller.handle_mouse_wheel.assert_called_with(-120)

    def test_on_mousewheel_not_0(self, setup, mocker):
        """
        Test when the mousewheel is used and event.num is 0 and event.delta is
        not 0

        :test_condition: controller.handle_mouse_wheel is called with
        event.delta

        :param setup: setup
        :param mocker: mocker
        :returns: None
        """
        window = MainWindow(self.mock_controller, MagicMock())

        event = MagicMock()
        event.num = 0
        event.delta = 120

        window.on_mousewheel(event)

        self.mock_controller.handle_mouse_wheel.assert_called_with(120)

    def test_on_drag(self, setup, mocker):
        """
        Test when the mouse is dragged

        :test_condition: controller.handle_motion() is called

        :param setup: setup
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())

        window.on_drag(MagicMock())

        self.mock_controller.handle_motion.assert_called()

    def test_on_motion_not_zoom(self, setup, mocker):
        """
        Test when the mouse is moved and zoom and flood cursor are false

        :test_condition: draw_brush() is called
        :param setup: setup
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())
        window.zoom_cursor = False
        window.flood_cursor = False
        event = MagicMock()
        event.x = 5
        event.y = 3

        spy = mocker.spy(window, 'draw_brush')

        window.on_motion(event)

        spy.assert_called()

    def test_on_motion_zoom(self, setup, mocker):
        """
        Test when the mouse is moved and zoom_cursor is true

        :test_condition: draw_brush() is not called

        :param setup: setup
        :param mocker: mocker
        :returns: None
        """
        window = MainWindow(self.mock_controller, MagicMock())
        window.zoom_cursor = True

        spy = mocker.spy(window, 'draw_brush')

        window.on_motion(MagicMock())

        spy.assert_not_called()

    def test_draw_brush_not_none_brush(self, setup, mocker):
        """
        Test drawing the brush

        :test_condition: canvas.delete is called

        :param setup: setup
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())
        window.canvas = MagicMock()

        window.brush_cursor = True
        window.draw_brush((10, 10))

        window.canvas.delete.assert_called_once()

    def test_draw_brush_not_none(self, setup, mocker):
        """
        Test drawing the brush

        :test_condition: canvas.draw_oval is called

        :param setup: setup
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())
        window.canvas = MagicMock()

        window.brush_cursor = None
        window.draw_brush((10, 10))

        window.canvas.create_oval.assert_called_once()

    def test_draw_brush_none_pos(self, setup, mocker):
        """
        Test drawing brush when position is none

        :test_condition: canvas.create_oval is called

        :param setup: setup
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())
        window.canvas = MagicMock()

        window.draw_brush(None)

        window.canvas.create_oval.assert_called_once()

    def test_draw_brush_pos(self, setup, mocker):
        """
        Test drawing the brush with a position

        :test_condition: canvas.create_oval is called

        :param setup: setup
        :param mocker: mocker
        :returns: None
        """
        window = MainWindow(self.mock_controller, MagicMock())
        window.canvas = MagicMock()

        window.draw_brush((10, 10))

        window.canvas.create_oval.assert_called_once()

    def test_on_click(self, setup, mocker):
        """
        Test on click

        :test_condition: controller.handle_left_click() is called

        :param setup: setup
        :param mocker: mocker
        :returns: None
        """
        window = MainWindow(self.mock_controller, MagicMock())

        event = MagicMock()
        event.x = 21
        event.y = 42

        window.on_click(event)

        self.mock_controller.handle_left_click.called_with((21, 42))

    def test_on_click_no_draw(self, setup, mocker):
        """
        Test on click

        :test_condition: controller.handle_left_click() is called

        :param setup: setup
        :param mocker: mocker
        :returns: None
        """
        window = MainWindow(self.mock_controller, MagicMock())

        event = MagicMock()
        event.x = 21
        event.y = 42
        window.can_draw = False

        window.on_click(event)

        self.mock_controller.handle_left_click.assert_not_called()

    def test_set_brush_radius(self, setup, mocker):
        """
        Test changing the brush radius

        :test_condition: brush_radius is changed

        :param setup: setup
        :param mocker: mocker
        :returns: None
        """
        window = MainWindow(self.mock_controller, MagicMock())

        window.set_brush_radius(19)

        assert window.brush_radius == 19

    def test_on_enter_canvas_zoom(self, setup, mocker):
        """
        Test when the mouse enters the canvas and zoom_cursor is true

        :test_condition: self.canvas.config() is called

        :param setup: setup
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())
        event = MagicMock()

        window.zoom_cursor = True
        window.canvas = MagicMock()

        window.on_enter_canvas(event)
        window.canvas.config.assert_called_once()

    def test_on_enter_canvas_flood(self, setup, mocker):
        """
        Test when the mouse enters the canvas and flood_cursor is true

        :test_condition: self.canvas.config() is called

        :param setup: setup
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())
        event = MagicMock()

        window.flood_cursor = True
        window.canvas = MagicMock()

        window.on_enter_canvas(event)
        window.canvas.config.assert_called_once()

    def test_on_enter_canvas_other(self, setup, mocker):
        """
        Test when the mouse enters the canvas and zoom_cursor and food_cursor
        are both false

        :test_condition: self.canvas.config() is called

        :param setup: setup
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())
        event = MagicMock()

        window.canvas = MagicMock()

        window.on_enter_canvas(event)
        window.canvas.config.assert_called_once()

    def test_on_leave_canvas(self, setup, mocker):
        """
        Test when the mouse leaves the canvas

        :param setup: setup
        :param mocker: mocker
        :returns: None
        """

        window = MainWindow(self.mock_controller, MagicMock())

        window.on_leave_canvas(MagicMock())

    def test_start_progressbar(self, setup, mocker):
        """
        Test starting the progressbar

        :test_condition: prog_popup.pack_slaves() is called

        :param setup: setup
        :param mocker: mocker
        :returns: None
        """

        mocker.patch('tkinter.Toplevel', return_value=MagicMock())
        mocker.patch('tkinter.Label')
        mocker.patch('tkinter.ttk.Progressbar')
        mocker.patch('tkinter.DoubleVar')

        window = MainWindow(self.mock_controller, MagicMock())
        window.start_progressbar(10)

        window.prog_popup.pack_slaves.assert_called()


class TestAboutDialog():

    def test_on_version_click(self, mocker):
        """
        Test when the version link is clicked

        :test_condition: webbrowser.open() is called
        :param mocker: Mocker
        :returns: None
        """
        web_mock = mocker.patch('webbrowser.open')
        mocker.patch('tkinter.Toplevel')
        mocker.patch("friendly_ground_truth.version_info."
                     "VersionInfo.check_for_update")
        mocker.patch("friendly_ground_truth.version_info"
                     ".VersionInfo.check_newer_version",
                     return_value=True)
        mocker.patch("friendly_ground_truth.version_info.VersionInfo."
                     "get_newest_release_info")
        mocker.patch('tkinter.Label')

        dialog = AboutDialog()

        dialog.on_version_click(MagicMock())

        web_mock.assert_called()

    def test_on_manual_click(self, mocker):
        """
        Test when the manual link is clicked

        :test_condition: webbrowser.open() is called
        :param mocker: Mocker
        :returns: None
        """
        web_mock = mocker.patch('webbrowser.open')
        mocker.patch('tkinter.Toplevel')
        mocker.patch("friendly_ground_truth.version_info."
                     "VersionInfo.check_for_update")
        mocker.patch("friendly_ground_truth.version_info"
                     ".VersionInfo.check_newer_version",
                     return_value=True)
        mocker.patch("friendly_ground_truth.version_info.VersionInfo."
                     "get_newest_release_info")
        mocker.patch('tkinter.Label')

        dialog = AboutDialog()

        dialog.on_manual_click(MagicMock())

        web_mock.assert_called()

    def test_on_bug_click(self, mocker):
        """
        Test when the bug link is clicked

        :test_condition: webbrowser.open() is called
        :param mocker: Mocker
        :returns: None
        """
        web_mock = mocker.patch('webbrowser.open')
        mocker.patch('tkinter.Toplevel')
        mocker.patch("friendly_ground_truth.version_info."
                     "VersionInfo.check_for_update")
        mocker.patch("friendly_ground_truth.version_info"
                     ".VersionInfo.check_newer_version",
                     return_value=False)
        mocker.patch("friendly_ground_truth.version_info.VersionInfo."
                     "get_newest_release_info")
        mocker.patch('tkinter.Label')

        dialog = AboutDialog()

        dialog.on_bug_click(MagicMock())

        web_mock.assert_called()


class TestKeyboardShortcuts():

    def test_init(self, mocker):
        """
        Test creating the dialog

        :param mocker: Mocker
        :returns: None
        """
        mocker.patch('tkinter.Toplevel')
        mocker.patch('tkinter.Label')
        mocker.patch('tkinter.PhotoImage')
        dialog = KeyboardShortcutDialog()

        assert dialog is not None
