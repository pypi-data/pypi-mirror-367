import tkinter as tk
from tkinter import filedialog

def open_file():
    return filedialog.askopenfilename()

def save_file():
    return filedialog.asksaveasfilename()

def select_directory():
    return filedialog.askdirectory()