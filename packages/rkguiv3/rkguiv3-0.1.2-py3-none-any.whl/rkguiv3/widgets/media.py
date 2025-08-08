import tkinter as tk
import vlc

class VideoPlayer(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.player.set_hwnd(self.winfo_id())

class AudioPlayer(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

class ImageView(tk.Label):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
    
    def load_image(self, path):
        from PIL import Image, ImageTk
        img = Image.open(path)
        self.image = ImageTk.PhotoImage(img)
        self.config(image=self.image)