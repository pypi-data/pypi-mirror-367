class DragDropMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.drag_data = {"x": 0, "y": 0}
        self.bind("<ButtonPress-1>", self.on_drag_start)
        self.bind("<B1-Motion>", self.on_drag_motion)
    
    def on_drag_start(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
    
    def on_drag_motion(self, event):
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        self.place(x=self.winfo_x() + dx, y=self.winfo_y() + dy)