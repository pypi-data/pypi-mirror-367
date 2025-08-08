import tkinter as tk
from tkinter import ttk

class MenuBar(tk.Menu):
    def add_menu(self, label, items):
        menu = tk.Menu(self, tearoff=0)
        for item in items:
            if item == "separator":
                menu.add_separator()
            else:
                menu.add_command(label=item["label"], command=item["command"])
        self.add_cascade(label=label, menu=menu)

class ContextMenu(tk.Menu):
    def __init__(self, master, items):
        super().__init__(master, tearoff=0)
        for item in items:
            if item == "separator":
                self.add_separator()
            else:
                self.add_command(label=item["label"], command=item["command"])
    
    def show(self, event):
        self.post(event.x_root, event.y_root)