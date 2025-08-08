import tkinter as tk
from tkinter import ttk

class GUIApp(tk.Tk):
    def __init__(self, title="rkguiv2", theme="light", size=(800, 600)):
        super().__init__()
        self.title(title)
        self.geometry(f"{size[0]}x{size[1]}")
        self.style = ttk.Style()
        self.set_theme(theme)
    
    def set_theme(self, theme_name):
        if theme_name == "dark":
            self.style.theme_use("alt")
            self.configure(bg="#333")
        else:
            self.style.theme_use("clam")
    
    def start(self):
        self.mainloop()