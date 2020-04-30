"""
File Name: make_icns.py

Authors: Kyle Seidenthal

Date: 30-04-2020

Description: Script to convert the ico file to icns

"""

import imageio as io

img = io.imread('icon.ico')
io.imsave('icon.icns', img)
