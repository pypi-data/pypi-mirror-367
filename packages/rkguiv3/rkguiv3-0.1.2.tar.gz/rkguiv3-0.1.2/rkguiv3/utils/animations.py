import tkinter as tk

def fade_in(widget, duration=1000):
    widget.attributes("-alpha", 0.0)
    widget.update()
    
    def step(alpha):
        alpha += 0.05
        if alpha < 1.0:
            widget.attributes("-alpha", alpha)
            widget.after(int(duration/20), lambda: step(alpha))
        else:
            widget.attributes("-alpha", 1.0)
    
    step(0.0)

def slide_in(widget, start_x, end_x, duration=1000):
    widget.place(x=start_x)
    
    def step(x):
        step_size = (end_x - x) / 10
        new_x = x + step_size
        if abs(new_x - end_x) > 1:
            widget.place(x=new_x)
            widget.after(int(duration/20), lambda: step(new_x))
        else:
            widget.place(x=end_x)
    
    step(start_x)