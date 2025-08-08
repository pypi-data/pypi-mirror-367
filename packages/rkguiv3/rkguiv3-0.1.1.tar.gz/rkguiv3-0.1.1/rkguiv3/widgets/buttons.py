import tkinter as tk
from PIL import Image, ImageTk

class ImageButton(tk.Button):
    def __init__(self, master, image_path, command=None, **kwargs):
        img = Image.open(image_path)
        self.img = ImageTk.PhotoImage(img)
        super().__init__(master, image=self.img, command=command, **kwargs)

class ToggleButton(ttk.Checkbutton):
    def __init__(self, master, text="", **kwargs):
        self.var = tk.BooleanVar()
        super().__init__(master, text=text, variable=self.var, **kwargs)
    
    def get_state(self):
        return self.var.get()

class LikeButton(tk.Button):
    def __init__(self, master, **kwargs):
        self.liked = False
        super().__init__(master, text="♡", command=self.toggle, **kwargs)
    
    def toggle(self):
        self.liked = not self.liked
        self.config(text="♥" if self.liked else "♡")