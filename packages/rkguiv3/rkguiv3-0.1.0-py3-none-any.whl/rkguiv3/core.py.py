import tkinter as tk
from .widgets import *
from .dialogs import *
from .utils import *

class GUIApp(tk.Tk):
    def __init__(self, title="My GUI App"):
        super().__init__()
        self.title(title)
        self.geometry("800x600")
        
        # Инициализация тем
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Регистрация компонентов
        self.widgets = {}
    
    def add_widget(self, name, widget):
        self.widgets[name] = widget
        return widget
    
    def start(self):
        self.mainloop()
    
    def enable_debug(self):
        set_debug_mode(True)
    
    def disable_debug(self):
        set_debug_mode(False)