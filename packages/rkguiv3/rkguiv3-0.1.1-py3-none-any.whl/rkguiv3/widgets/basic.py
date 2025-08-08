import tkinter as tk
from tkinter import ttk

class Label(tk.Label):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

class TextEdit(tk.Text):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.scrollbar = ttk.Scrollbar(master, command=self.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.config(yscrollcommand=self.scrollbar.set)

class PathInput(ttk.Entry):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.browse_btn = ttk.Button(master, text="...", width=3, command=self.browse)
        self.browse_btn.pack(side=tk.RIGHT)
    
    def browse(self):
        from ..dialogs.file_dialogs import open_file
        path = open_file()
        if path:
            self.delete(0, tk.END)
            self.insert(0, path)