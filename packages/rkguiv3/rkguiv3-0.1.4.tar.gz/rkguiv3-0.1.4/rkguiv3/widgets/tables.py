import tkinter as tk
from tkinter import ttk

class ScheduleTable(ttk.Treeview):
    def __init__(self, master, columns, **kwargs):
        super().__init__(master, columns=columns, show="headings", **kwargs)
        for col in columns:
            self.heading(col, text=col)
            self.column(col, width=100)
    
    def add_row(self, values):
        self.insert("", tk.END, values=values)