import tkinter as tk
from tkinter import messagebox

def show_alert(title, message):
    messagebox.showwarning(title, message)

def show_error(title, message):
    messagebox.showerror(title, message)

def show_info(title, message):
    messagebox.showinfo(title, message)

def show_confirm(title, message):
    return messagebox.askyesno(title, message)