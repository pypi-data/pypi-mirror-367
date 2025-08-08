import tkinter as tk
from tkinter import ttk

class Dropdown(ttk.Combobox):
    def __init__(self, master, options=[], **kwargs):
        super().__init__(master, values=options, **kwargs)
        self.set(options[0] if options else "")
    
    def get_selected(self):
        return self.get()