"""
File Name: friendly_ground_truth.py

Authors: Kyle Seidenthal

Date: 20-02-2020

Description: The entry point for the application

"""

import wx
from controller.controller import Controller

if __name__ == '__main__':
    app = wx.App(False)

    controller = Controller()

    app.MainLoop()
