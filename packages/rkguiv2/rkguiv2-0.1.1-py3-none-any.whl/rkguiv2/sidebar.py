import tkinter as tk

class Sidebar(tk.Frame):
    def __init__(self, parent, width=200):
        super().__init__(parent.tk if hasattr(parent, "tk") else parent, width=width, bg="#ccc")
        self.pack(side="left", fill="y")
