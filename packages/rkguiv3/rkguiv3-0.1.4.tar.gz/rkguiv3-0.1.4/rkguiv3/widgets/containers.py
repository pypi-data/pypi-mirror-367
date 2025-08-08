import tkinter as tk
from tkinter import ttk

class FrameContainer(ttk.Frame):
    """Простой контейнер-фрейм для группировки виджетов"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.pack_propagate(False)  # Запрещаем изменение размера контейнера

    def add_widget(self, widget, **pack_options):
        """Добавляет виджет в контейнер"""
        widget.pack(in_=self, **pack_options)
        return widget

class TabView(ttk.Notebook):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
    
    def add_tab(self, title, widget=None):
        frame = ttk.Frame(self)
        if widget:
            widget.pack(fill=tk.BOTH, expand=True)
        self.add(frame, text=title)
        return frame

class ScrollContainer(tk.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.scrollbar = ttk.Scrollbar(master, orient="vertical", command=self.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.configure(yscrollcommand=self.scrollbar.set)
        self.inner_frame = ttk.Frame(self)
        self.create_window((0, 0), window=self.inner_frame, anchor="nw")
        self.inner_frame.bind("<Configure>", self.on_frame_configure)
    
    def on_frame_configure(self, event):
        self.configure(scrollregion=self.bbox("all"))

class DockPanel(ttk.PanedWindow):
    def add_panel(self, widget, **kwargs):
        self.add(widget, **kwargs)

class ResizablePanel(ttk.PanedWindow):
    def __init__(self, master, orientation="horizontal", **kwargs):
        super().__init__(master, orient=orientation, **kwargs)
