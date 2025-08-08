import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar, DateEntry

class RatingStars(tk.Frame):
    def __init__(self, master, max_stars=5, **kwargs):
        super().__init__(master, **kwargs)
        self.stars = []
        self.value = 0
        for i in range(max_stars):
            star = tk.Label(self, text="☆", font=("Arial", 20))
            star.bind("<Button-1>", lambda e, idx=i: self.set_rating(idx + 1))
            star.pack(side=tk.LEFT)
            self.stars.append(star)
    
    def set_rating(self, value):
        self.value = value
        for i, star in enumerate(self.stars):
            star.config(text="★" if i < value else "☆")

class CalendarInput(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.entry = ttk.Entry(self)
        self.entry.pack(side=tk.LEFT)
        self.cal_btn = ttk.Button(self, text="📅", command=self.show_calendar)
        self.cal_btn.pack(side=tk.LEFT)
    
    def show_calendar(self):
        top = tk.Toplevel(self)
        cal = Calendar(top, selectmode="day")
        cal.pack(padx=10, pady=10)
        ttk.Button(top, text="OK", command=lambda: self.set_date(cal.get_date())).pack()
    
    def set_date(self, date):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, date)
        self.focus_set()