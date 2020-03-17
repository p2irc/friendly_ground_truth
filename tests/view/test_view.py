"""
File Name: test_view.py

Authors: Kyle Seidenthal

Date: 12-03-2020

Description: Test cases for the view

"""
import pytest
import wx

from mock import MagicMock, PropertyMock

from friendly_ground_truth.view.view import MainWindow


class TestView():
    """
    Test cases for the View
    """

    @pytest.fixture
    def setup(self, mocker):
        self.mock_frame = mocker.patch('wx.Frame.__init__')
        mocker.patch('wx.GetApp')
        mocker.patch('wx.App.Bind')
        mocker.patch('wx.Frame.Bind')

        self.mock_controller = mocker.patch('friendly_ground_truth.' +
                                            'controller.controller.Controller')

    @pytest.fixture
    def mock_init_ui(self, mocker):

        mocker.patch('friendly_ground_truth.view.view.MainWindow.init_ui')

    @pytest.fixture
    def mock_painting(self, mocker):

        mocker.patch('wx.DCOverlay')
        mocker.patch('wx.Image')
        mocker.patch('wx.Bitmap')
        mocker.patch('wx.Pen')
        mocker.patch('wx.Brush')

    def test_init_ui(self, setup, mock_painting,  mocker):
        """
        Test that the ui is initialized

        :test_condition: the window's tool_bar and image_panel are not None

        :param setup: The setup fixture
        :param mocker: Mocker
        :returns: None
        """
        mocker.patch('wx.MenuBar')
        mocker.patch('wx.Menu')
        mocker.patch('wx.MenuItem')
        mocker.patch('wx.AcceleratorEntry')
        mocker.patch('wx.AcceleratorTable')
        mocker.patch('wx.Window.SetAcceleratorTable')
        mocker.patch('wx.Frame.CreateToolBar')
        mocker.patch('wx.Panel')
        mocker.patch('wx.Frame.SetMenuBar')
        mocker.patch('wx.Frame.SetSize')
        mocker.patch('wx.Frame.Centre')

        window = MainWindow(self.mock_controller)

        window.init_ui()

        assert window.image_panel is not None
        assert window.tool_bar is not None

    def test_show_image_dc_none(self, setup, mock_init_ui, mock_painting,
                                mocker):
        """
        Test showing an image with a None dc

        :test_condition: dc.DrawBitmap() is called

        :returns: None
        """

        mocker.patch('wx.Image')
        mocker.patch('wx.Bitmap')
        mocker.patch('wx.DCOverlay')

        mocker.patch.object(wx.ClientDC, '__init__', return_value=None)
        mocker.patch.object(wx.ClientDC, 'SetUserScale')
        mock_dc = mocker.patch.object(wx.ClientDC, 'DrawBitmap',  create=True)

        window = MainWindow(self.mock_controller)
        window.image_panel = MagicMock()
        window.overlay = MagicMock()

        img = MagicMock()

        window.show_image(img, None)

        mock_dc.assert_called()

    def test_show_image_dc(self, setup, mock_init_ui, mocker):
        """
        Test showing an image with a not-None dc

        :test_condition: dc.DrawBitmap() is called

        :returns: none
        """
        mocker.patch('wx.Image')
        mocker.patch('wx.Bitmap')

        window = MainWindow(self.mock_controller)
        img = MagicMock()
        dc = MagicMock()

        window.show_image(img, dc)

        dc.DrawBitmap.assert_called()

    def test_menu_handler_open(self, setup, mock_init_ui, mocker):
        """
        Test when the menu handler is called and the events id is wx.ID_OPEN

        :test_condition: controller.load_new_image() is called

        :returns: None
        """

        window = MainWindow(self.mock_controller)
        window.tool_bar = MagicMock()

        event = MagicMock()
        event.GetId.return_value = wx.ID_OPEN

        window.menu_handler(event)

        self.mock_controller.load_new_image.assert_called()

    def test_menu_handler_save(self, setup, mock_init_ui, mocker):
        """
        Test when the menu handler is called and the event id is wx.ID_SAVE

        :test_condition: controller.save_mask() is called

        :returns: None
        """

        window = MainWindow(self.mock_controller)
        window.tool_bar = MagicMock()

        event = MagicMock()
        event.GetId.return_value = wx.ID_SAVE

        window.menu_handler(event)

        self.mock_controller.save_mask.assert_called()

    def test_menu_handler_thresh(self, setup, mock_init_ui, mocker):
        """
        Test when the menu handler is called and the event id is ID_TOOL_THRESH

        :test_condition: controller.change_mode() is called with ID_TOOL THRESH

        :returns: None
        """

        window = MainWindow(self.mock_controller)
        window.tool_bar = MagicMock()

        event = MagicMock()
        event.GetId.return_value = window.ID_TOOL_THRESH

        window.menu_handler(event)

        self.mock_controller.change_mode.assert_called_with(window.
                                                            ID_TOOL_THRESH)

    def test_menu_handler_add(self, setup, mock_init_ui, mocker):
        """
        Test when the menu handler is called and the event_id is ID_TOOL_ADD

        :test_condition: controller.change_mode() is called with ID_TOOL_ADD

        :returns: None
        """

        window = MainWindow(self.mock_controller)
        window.tool_bar = MagicMock()

        event = MagicMock()
        event.GetId.return_value = window.ID_TOOL_ADD

        window.menu_handler(event)

        self.mock_controller.change_mode.assert_called_with(window.
                                                            ID_TOOL_ADD)

    def test_menu_handler_remove(self, setup, mock_init_ui, mocker):
        """
        Test when the menu handler is called and the event_id is ID_TOOL_REMOVE

        :test_condition: controller.change_mode() is called with ID_TOOL_REMOVE

        :returns: None
        """

        window = MainWindow(self.mock_controller)
        window.tool_bar = MagicMock()

        event = MagicMock()
        event.GetId.return_value = window.ID_TOOL_REMOVE

        window.menu_handler(event)

        self.mock_controller.change_mode.assert_called_with(window.
                                                            ID_TOOL_REMOVE)

    def test_menu_handler_no_root(self, setup, mock_init_ui, mocker):
        """
        Test when the menu handler is called and the event_id is
        ID_TOOL_NO_ROOT

        :test_condition: controller.change_mode() is called with
                         ID_TOOL_NO_ROOT

        :returns: None
        """

        window = MainWindow(self.mock_controller)
        window.tool_bar = MagicMock()

        event = MagicMock()
        event.GetId.return_value = window.ID_TOOL_NO_ROOT

        window.menu_handler(event)

        self.mock_controller.change_mode.assert_called_with(window.
                                                            ID_TOOL_NO_ROOT)

    def test_menu_handler_next_image(self, setup, mock_init_ui, mocker):
        """
        Test when the menu handler is called and the event_id is
        ID_TOOL_NEXT_IMAGE

        :test_condition: controller.change_mode() is called with
                         ID_TOOL_NEXT_IMAGE

        :returns: None
        """

        window = MainWindow(self.mock_controller)
        window.tool_bar = MagicMock()

        event = MagicMock()
        event.GetId.return_value = window.ID_TOOL_NEXT_IMAGE

        window.menu_handler(event)

        self.mock_controller.change_mode.assert_called_with(window.
                                                            ID_TOOL_NEXT_IMAGE)

    def test_menu_handler_prev_image(self, setup, mock_init_ui, mocker):
        """
        Test when the menu handler is called and the event_id is
        ID_TOOL_PREV_IMAGE

        :test_condition: controller.change_mode() is called with
                         ID_TOOL_PREV_IMAGE

        :returns: None
        """

        window = MainWindow(self.mock_controller)
        window.tool_bar = MagicMock()

        event = MagicMock()
        event.GetId.return_value = window.ID_TOOL_PREV_IMAGE

        window.menu_handler(event)

        self.mock_controller.change_mode.assert_called_with(window.
                                                            ID_TOOL_PREV_IMAGE)

    def test_menu_handler_invalid(self, setup, mock_init_ui, mocker):
        """
        Test when the menu handler is called and the event_id is
        None

        :test_condition: Returns None

        :returns: None
        """

        window = MainWindow(self.mock_controller)
        window.tool_bar = MagicMock()

        event = MagicMock()
        event.GetId.return_value = None

        result = window.menu_handler(event)

        assert None is result

    def test_on_key_A(self, setup, mock_init_ui, mocker):
        """
        Test when the on_key handler is called and the keycode was ord('A') or
        wx.WXK_LEFT

        :test_condition: controller.prev_patch() is called

        :returns: None
        """

        window = MainWindow(self.mock_controller)

        event = MagicMock()
        event.GetKeyCode.return_value = wx.WXK_LEFT

        window.on_key(event)

        self.mock_controller.prev_patch.assert_called()

        event.GetKeyCode.return_Value = ord('A')

        window.on_key(event)

        self.mock_controller.prev_patch.assert_called()

    def test_on_key_D(self, setup, mock_init_ui, mocker):
        """
        Test when the on_key handler is called and the keycode was ord('D') or
        wx.WXK_RIGHT

        :test_condition: controller.next_patch() is called

        :returns: None
        """

        window = MainWindow(self.mock_controller)

        event = MagicMock()
        event.GetKeyCode.return_value = wx.WXK_RIGHT

        window.on_key(event)

        self.mock_controller.next_patch.assert_called()

        event.GetKeyCode.return_Value = ord('D')

        window.on_key(event)

        self.mock_controller.next_patch.assert_called()

    def test_on_key_None(self, setup, mock_init_ui, mocker):
        """
        Test when the on_key handler is called and the keycode was None

        :test_condition: event.Skip() was called

        :returns: None
        """

        window = MainWindow(self.mock_controller)

        event = MagicMock()
        event.GetKeyCode.return_value = None

        window.on_key(event)

        event.Skip.assert_called()

    def test_on_tool_chosen_thresh(self, setup, mock_init_ui, mocker):
        """
        Test when the on_tool_chosen hanlder is called and the event_id is
        ID_TOOL_THRESH

        :test_condition: controller.change_mode() is called with ID_TOOL_THRESH

        :returns: None
        """

        window = MainWindow(self.mock_controller)

        event = MagicMock()
        event.GetId.return_value = window.ID_TOOL_THRESH

        window.on_tool_chosen(event)

        self.mock_controller.change_mode.assert_called_with(window.
                                                            ID_TOOL_THRESH)

    def test_on_tool_chosen_add(self, setup, mock_init_ui, mocker):
        """
        Test when the on_tool_chosen handler is called and the event_id is
        ID_TOOL_ADD

        :test_condition: controller.change_mode() is called with ID_TOOL_ADD

        :returns: None
        """

        window = MainWindow(self.mock_controller)

        event = MagicMock()
        event.GetId.return_value = window.ID_TOOL_ADD

        window.on_tool_chosen(event)

        self.mock_controller.change_mode.assert_called_with(window.
                                                            ID_TOOL_ADD)

    def test_on_tool_chosen_remove(self, setup, mock_init_ui, mocker):
        """
        Test when the on_tool_chosen handler is called and the event_id is
        ID_TOOL_REMOVE

        :test_condition: controller.change_mode() is called with ID_TOOL_REMOVE

        :returns: None
        """

        window = MainWindow(self.mock_controller)

        event = MagicMock()
        event.GetId.return_value = window.ID_TOOL_REMOVE

        window.on_tool_chosen(event)

        self.mock_controller.change_mode.assert_called_with(window.
                                                            ID_TOOL_REMOVE)

    def test_on_tool_chosen_no_root(self, setup, mock_init_ui, mocker):
        """
        Test when the on_tool_chosen handler is called and the event_id is
        ID_TOOL_NO_ROOT

        :test_condition: controller.change_mode() is called with
                         ID_TOOL_NO_ROOT

        :returns: None
        """

        window = MainWindow(self.mock_controller)

        event = MagicMock()
        event.GetId.return_value = window.ID_TOOL_NO_ROOT

        window.on_tool_chosen(event)

        self.mock_controller.change_mode.assert_called_with(window.
                                                            ID_TOOL_NO_ROOT)

    def test_on_tool_chosen_next(self, setup, mock_init_ui, mocker):
        """
        Test when the on_tool_chosen handler is called and the event_id is
        ID_TOOL_NEXT_IMAGE

        :test_condition: controller.next_patch() is called

        :returns: None
        """

        window = MainWindow(self.mock_controller)

        event = MagicMock()
        event.GetId.return_value = window.ID_TOOL_NEXT_IMAGE

        window.on_tool_chosen(event)

        self.mock_controller.next_patch.assert_called()

    def test_on_tool_chosen_prev(self, setup, mock_init_ui, mocker):
        """
        Test when the on_tool_chosen handler is called and the event_id is
        ID_TOOL_PREV_IMAGE

        :test_condition: controller.prev_patch() is called

        :returns: None
        """

        window = MainWindow(self.mock_controller)

        event = MagicMock()
        event.GetId.return_value = window.ID_TOOL_PREV_IMAGE

        window.on_tool_chosen(event)

        self.mock_controller.prev_patch.assert_called()

    def test_on_tool_chosen_invalid(self, setup, mock_init_ui, mocker):
        """
        Test when the on_tool_chosen handler is called and the event_id is a
        garbage value (like -1)

        :test_condition: returns False

        :returns: None
        """

        window = MainWindow(self.mock_controller)

        event = MagicMock()
        event.GetId.return_value = -1

        result = window.on_tool_chosen(event)

        assert False is result

    def test_on_mousewheel(self, setup, mock_init_ui, mocker):
        """
        Test when the mousewheel handler is called

        :test_condition: controller.handle_mouse_wheel() is called

        :returns: None
        """

        window = MainWindow(self.mock_controller)

        event = MagicMock()

        window.on_mousewheel(event)

        self.mock_controller.handle_mouse_wheel.assert_called()

    def test_set_brush_radius(self, setup, mock_init_ui, mocker):
        """
        Test when the set_brush_radius handler is called

        :test_condition: the brush_radius is updated

        :returns: None
        """

        window = MainWindow(self.mock_controller)

        window.set_brush_radius(21)

        assert 21 == window.brush_radius

        window.set_brush_radius(2)

        assert 2 == window.brush_radius

    def test_on_left_down(self, setup, mock_init_ui, mocker):
        """
        Test when the left mouse button is pressed

        :test_condition: controller.handle_left_click() is called
                         with the proper mouse position, converted to image
                         coordinates
        :returns: None
        """

        def mock_screen_to_client(in_position):
            return in_position[0] + 1, in_position[1] + 1

        def mock_screen_pos():
            return (0, 0)

        mocker.patch('wx.Panel.ScreenToClient',
                     side_effect=mock_screen_to_client)

        mocker.patch('wx.Panel.GetScreenPosition', side_effect=mock_screen_pos)

        window = MainWindow(self.mock_controller)
        window.image_panel = MagicMock()

        event = MagicMock()
        event.GetPosition.return_value = (1, 1)

        expected = window.convert_mouse_to_img_pos(event.GetPosition())

        window.on_left_down(event)

        self.mock_controller.handle_left_click.assert_called_with(expected)

    def test_on_left_up(self, setup, mock_init_ui, mocker):
        """
        Test when the left mouse button is released

        :test_condition: controller.handle_left_release() is called

        :returns: None
        """

        window = MainWindow(self.mock_controller)

        window.on_left_up(None)

        self.mock_controller.handle_left_release.assert_called()

    def test_on_motion_not_dragging(self, setup, mock_init_ui, mocker):
        """
        Test when the mouse is moved and event.Dragging() and
        event.LeftIsDown() are both false

        :test_condition: controller.handle_motion() is NOT called

        :returns: None
        """

        event = MagicMock()
        event.Dragging = PropertyMock(return_value=False)
        event.LeftIsDown = PropertyMock(return_value=False)

        mocker.patch('wx.Panel.GetScreenPosition')
        mocker.patch('wx.Window.ScreenToClient')

        window = MainWindow(self.mock_controller)
        window.image_panel = MagicMock()

        window.on_motion(event)

        self.mock_controller.handle_motion.assert_not_called()

    def test_on_motion_dragging(self, setup, mock_init_ui, mocker):
        """
        Test when the mouse is moved and event.Dragging() and
        event.LeftIsDown() are both true

        :test_condition: controller.handle_motion() is called

        :returns: None
        """

        event = MagicMock()
        event.Dragging = PropertyMock(return_value=True)
        event.LeftIsDown = PropertyMock(return_value=True)

        mocker.patch('wx.Panel.GetScreenPosition')
        mocker.patch('wx.Window.ScreenToClient')

        window = MainWindow(self.mock_controller)
        window.image_panel = MagicMock()

        window.on_motion(event)

        self.mock_controller.handle_motion.assert_called()

    def test_on_enter_panel(self, setup, mock_init_ui, mocker, mock_painting):
        """
        Test when the mouse enters the panel

        :test_condition: self.SetCursor() is called with
        wx.StockCursor(wx.CURSOR_BLANK)

        :returns: None
        """

        mock_cursor = mocker.patch.object(MainWindow, "SetCursor")
        mocker.patch('wx.StockCursor')

        window = MainWindow(self.mock_controller)
        window.on_enter_panel(None)

        mock_cursor.assert_called_with(wx.StockCursor(wx.CURSOR_BLANK))

    def test_on_leave_panel(self, setup, mock_init_ui, mocker):
        """
        Test when the mouse leaves the panel

        :test_condition: wx.Cursor() is called with wx.CURSOR_DEFAULT

        :returns: None
        """

        mock_cursor = mocker.patch('wx.Cursor')

        window = MainWindow(self.mock_controller)
        window.on_leave_panel(None)

        mock_cursor.assert_called_with(wx.CURSOR_DEFAULT)

    def test_draw_brush_no_image(self, setup, mock_init_ui, mock_painting):
        """
        Test when the draw brush function is called and current_image is None

        :test_condition: Return None

        :returns: None
        """

        window = MainWindow(self.mock_controller)
        window.current_image = None

        result = window.draw_brush()

        assert result is None

    def test_draw_brush_no_pos(self, setup, mock_init_ui, mock_painting,
                               mocker):
        """
        Test when draw_brush() is called with no position

        :test_condition: dc.DrawCircle() is called with previous_mouse_position

        :returns: None
        """

        wx.PlatformInfo = ('wxMac')

        mocker.patch.object(wx.ClientDC, '__init__', return_value=None)
        mocker.patch.object(wx.ClientDC, 'SetPen')
        mocker.patch.object(wx.ClientDC, 'SetBrush')

        mock_dc = mocker.patch.object(wx.ClientDC, 'DrawCircle',  create=True)

        mocker.patch('friendly_ground_truth.view.view.MainWindow.show_image')

        previous_mouse_position = (1, 2)

        window = MainWindow(self.mock_controller)
        window.current_image = MagicMock()
        window.previous_mouse_position = previous_mouse_position
        window.image_panel = MagicMock()
        window.overlay = MagicMock()

        in_position = None

        window.draw_brush(in_position)

        mock_dc.assert_called_with(previous_mouse_position[0],
                                   previous_mouse_position[1],
                                   window.brush_radius)

    def test_draw_brush_with_pos(self, setup, mock_init_ui, mock_painting,
                                 mocker):
        """
        Test when draw_brush() is called with a position

        :test_condition: dc.DrawCircle() is called with position

        :returns: None
        """
        wx.PlatformInfo = ('wxMac')

        mocker.patch.object(wx.ClientDC, '__init__', return_value=None)
        mocker.patch.object(wx.ClientDC, 'SetPen')
        mocker.patch.object(wx.ClientDC, 'SetBrush')

        mock_dc = mocker.patch.object(wx.ClientDC, 'DrawCircle',  create=True)

        mocker.patch('friendly_ground_truth.view.view.MainWindow.show_image')

        window = MainWindow(self.mock_controller)
        window.current_image = MagicMock()
        window.previous_mouse_position = (0, 0)
        window.image_panel = MagicMock()
        window.overlay = MagicMock()

        in_position = (1, 1)

        window.draw_brush(in_position)

        mock_dc.assert_called_with(in_position[0], in_position[1],
                                   window.brush_radius)

    def test_draw_brush_wxMac(self, setup, mock_init_ui, mock_painting,
                              mocker):
        """
        Test when draw_brush() is called and 'wxMac' is not in wx.PlatformInfo

        :test_condition: wx.GCDC is called

        :returns: None
        """

        mocker.patch('wx.PlatformInfo', return_value=['wxSteve'])

        mocker.patch.object(wx.ClientDC, '__init__',
                            return_value=None)
        mocker.patch('friendly_ground_truth.view.view.MainWindow.show_image')
        mock_gcdc = mocker.patch('wx.GCDC')

        window = MainWindow(self.mock_controller)
        window.current_image = MagicMock()
        window.previous_mouse_position = (0, 0)
        window.image_panel = MagicMock()
        window.overlay = MagicMock()

        window.draw_brush()

        mock_gcdc.assert_called()

    def test_on_paint(self, setup, mock_init_ui, mocker):
        """
        Test when the on_paint function is called

        :test_condition: wx.DCOverlay is called

        :returns: None
        """

        mocker.patch('wx.ClientDC')
        mock_overlay = mocker.patch('wx.DCOverlay')

        window = MainWindow(self.mock_controller)
        window.image_panel = MagicMock()
        window.overlay = MagicMock()

        window.on_paint(None)

        mock_overlay.assert_called()

    def test_convert_mouse_to_img_pos(self, setup, mock_init_ui, mocker):
        """
        Test when convert_mouse_to_img_pos() is called

        :test_condition: the correct coordinates are output

        :returns: None
        """

        def mock_screen_to_client(in_position):
            return in_position[0] + 1, in_position[1] + 1

        def mock_screen_pos():
            return (0, 0)

        mocker.patch('wx.Panel.ScreenToClient',
                     side_effect=mock_screen_to_client)

        mocker.patch('wx.Panel.GetScreenPosition', side_effect=mock_screen_pos)

        window = MainWindow(self.mock_controller)
        image_panel = MagicMock()
        image_panel.ScreenToClient.side_effect = mock_screen_to_client
        image_panel.GetScreenPosition.side_effect = mock_screen_pos

        window.image_panel = image_panel

        pos = window.convert_mouse_to_img_pos((0, 0))

        assert pos == (1, 1)
