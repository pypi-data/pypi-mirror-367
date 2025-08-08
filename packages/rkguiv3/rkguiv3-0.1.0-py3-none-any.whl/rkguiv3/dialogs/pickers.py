import tkinter as tk
from tkinter import colorchooser, font

class ColorPicker:
    @staticmethod
    def choose_color():
        return colorchooser.askcolor()[1]

class FontChooser:
    @staticmethod
    def choose_font():
        return font.Font(font=font.families()[0], size=12)