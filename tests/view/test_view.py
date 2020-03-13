"""
File Name: test_view.py

Authors: Kyle Seidenthal

Date: 12-03-2020

Description: Test cases for the view

"""
import pytest
import os
import wx
import mock

from mock import MagicMock, PropertyMock

from friendly_ground_truth.controller.controller import Controller, Mode
from friendly_ground_truth.view.view import MainWindow


class TestView():
    """
    Test cases for the View
    """

    def test_show_image_dc_none(self):
        """
        Test showing an image with a None dc

        :test_condition: dc.DrawBitmap() is called

        :returns: None
        """

        assert False

    def test_show_image_dc(self):
        """
        Test showing an image with a not-None dc

        :test_condition: dc.DrawBitmap() is called

        :returns: none
        """

        assert False

    def test_menu_handler_open(self):
        """
        Test when the menu handler is called and the events id is wx.ID_OPEN

        :test_condition: controller.load_new_image() is called

        :returns: None
        """

        assert False

    def test_menu_handler_save(self):
        """
        Test when the menu handler is called and the event id is wx.ID_SAVE

        :test_condition: controller.save_mask() is called

        :returns: None
        """

        assert False

    def test_menu_handler_thresh(self):
        """
        Test when the menu handler is called and the event id is ID_TOOL_THRESH

        :test_condition: controller.change_mode() is called with ID_TOOL THRESH

        :returns: None
        """

        assert False

    def test_menu_handler_add(self):
        """
        Test when the menu handler is called and the event_id is ID_TOOL_ADD

        :test_condition: controller.change_mode() is called with ID_TOOL_ADD

        :returns: None
        """

        assert False

    def test_menu_handler_remove(self):
        """
        Test when the menu handler is called and the event_id is ID_TOOL_REMOVE

        :test_condition: controller.change_mode() is called with ID_TOOL_REMOVE

        :returns: None
        """

        assert False

    def test_menu_handler_no_root(self):
        """
        Test when the menu handler is called and the event_id is
        ID_TOOL_NO_ROOT

        :test_condition: controller.change_mode() is called with
                         ID_TOOL_NO_ROOT

        :returns: None
        """

        assert False

    def test_menu_handler_next_image(self):
        """
        Test when the menu handler is called and the event_id is
        ID_TOOL_NEXT_IMAGE

        :test_condition: controller.change_mode() is called with
                         ID_TOOL_NEXT_IMAGE

        :returns: None
        """

        assert False

    def test_menu_handler_prev_image(self):
        """
        Test when the menu handler is called and the event_id is
        ID_TOOL_PREV_IMAGE

        :test_condition: controller.change_mode() is called with
                         ID_TOOL_PREV_IMAGE

        :returns: None
        """

        assert False

    def test_on_key_A(self):
        """
        Test when the on_key handler is called and the keycode was ord('A') or
        wx.WXK_LEFT

        :test_condition: controller.prev_patch() is called

        :returns: None
        """

        assert False

    def test_on_key_D(self):
        """
        Test when the on_key handler is called and the keycode was ord('D') or
        wx.WXK_RIGHT

        :test_condition: controller.next_patch() is called

        :returns: None
        """

        assert False

    def test_on_tool_chosen_thresh(self):
        """
        Test when the on_tool_chosen hanlder is called and the event_id is
        ID_TOOL_THRESH

        :test_condition: controller.change_mode() is called with ID_TOOL_THRESH

        :returns: None
        """

        assert False

    def test_on_tool_chosen_add(self):
        """
        Test when the on_tool_chosen handler is called and the event_id is
        ID_TOOL_ADD

        :test_condition: controller.change_mode() is called with ID_TOOL_ADD

        :returns: None
        """

        assert False

    def test_on_tool_chosen_remove(self):
        """
        Test when the on_tool_chosen handler is called and the event_id is
        ID_TOOL_REMOVE

        :test_condition: controller.change_mode() is called with ID_TOOL_REMOVE

        :returns: None
        """

        assert False

    def test_on_tool_chosen_no_root(self):
        """
        Test when the on_tool_chosen handler is called and the event_id is
        ID_TOOL_NO_ROOT

        :test_condition: controller.change_mode() is called with
                         ID_TOOL_NO_ROOT

        :returns: None
        """

        assert False

    def test_on_tool_chosen_next(self):
        """
        Test when the on_tool_chosen handler is called and the event_id is
        ID_TOOL_NEXT_IMAGE

        :test_condition: controller.change_mode() is called with
                         ID_TOOL_NEXT_IMAGE

        :returns: None
        """

        assert False

    def test_on_tool_chosen_prev(self):
        """
        Test when the on_tool_chosen handler is called and the event_id is
        ID_TOOL_PREV_IMAGE

        :test_condition: controller.change_mode() is called with
                         ID_TOOL_PREV_IMAGE

        :returns: None
        """

        assert False

    def test_on_tool_chosen_invalid(self):
        """
        Test when the on_tool_chosen handler is called and the event_id is a
        garbage value (like -1)

        :test_condition: returns False

        :returns: None
        """

        assert False

    def test_on_mousewheel(self):
        """
        Test when the mousewheel handler is called

        :test_condition: controller.handle_mouse_wheel() is called

        :returns: None
        """

        assert False

    def test_set_brush_radius(self):
        """
        Test when the set_brush_radius handler is called

        :test_condition: the brush_radius is updated

        :returns: None
        """

        assert False

    def test_on_left_down(self):
        """
        Test when the left mouse button is pressed

        :test_condition: controller.handle_left_click() is called
                         with the proper mouse position, converted to image
                         coordinates
        :returns: None
        """

        assert False

    def test_on_left_up(self):
        """
        Test when the left mouse button is released

        :test_condition: controller.handle_left_release() is called

        :returns: None
        """

        assert False

    def test_on_motion_not_dragging(self):
        """
        Test when the mouse is moved and event.Dragging() and
        event.LeftIsDown() are both false

        :test_condition: controller.handle_motion() is NOT called

        :returns: None
        """

        assert False

    def test_on_motion_dragging(self):
        """
        Test when the mouse is moved and event.Dragging() and
        event.LeftIsDown() are both true

        :test_condition: controller.handle_motion() is called

        :returns: None
        """

        assert False

    def test_on_enter_panel(self):
        """
        Test when the mouse enters the panel

        :test_condition: self.SetCursor() is called

        :returns: None
        """

        assert False

    def test_on_leave_panel(self):
        """
        Test when the mouse leaves the panel

        :test_condition: wx.Cursor() is called with wx.CURSOR_DEFAULT

        :returns: None
        """

        assert False

    def test_draw_brush_no_image(self):
        """
        Test when the draw brush function is called and current_image is None

        :test_condition: Return None

        :returns: None
        """

        assert False

    def test_draw_brush_no_pos(self):
        """
        Test when draw_brush() is called with no position

        :test_condition: dc.DrawCircle() is called with previous_mouse_position

        :returns: None
        """

        assert False

    def test_draw_brush_with_pos(self):
        """
        Test when draw_brush() is called with a position

        :test_condition: dc.DrawCircle() is called with position

        :returns: None
        """

        assert False

    def test_draw_brush_wxMac(self):
        """
        Test when draw_brush() is called and 'wxMac' is in wx.PlatformInfo

        :test_condition: wx.GCDC is called

        :returns: None
        """

        assert False

    def test_on_paint(self):
        """
        Test when the on_paint function is called

        :test_condition: wx.DCOverlay is called

        :returns: none
        """

        assert False

    def test_convert_mouse_to_img_pos(self, mocker):
        """
        Test when convert_mouse_to_img_pos() is called

        :test_condition: the correct coordinates are output

        :returns: None
        """

        def mock_screen_to_client(in_position):
            return in_position[0] + 1, in_position[1] + 1

        def mock_screen_pos():
            return (0, 0)

        mock_controller = mocker.patch('friendly_ground_truth.' +
                                       'controller.controller.Controller')

        mocker.patch('wx.Panel.ScreenToClient',
                     side_effect=mock_screen_to_client)

        mocker.patch('wx.Panel.GetScreenPosition', side_effect=mock_screen_pos)

        mocker.patch('wx.Frame.__init__')

        mocker.patch('friendly_ground_truth.view.view.MainWindow.init_ui')

        mocker.patch('wx.GetApp')
        mocker.patch('wx.App.Bind')
        mocker.patch('wx.Frame.Bind')

        window = MainWindow(mock_controller)
        image_panel = MagicMock()
        image_panel.ScreenToClient.side_effect = mock_screen_to_client
        image_panel.GetScreenPosition.side_effect = mock_screen_pos

        window.image_panel = image_panel

        pos = window.convert_mouse_to_img_pos((0, 0))

        assert pos == (1, 1)
