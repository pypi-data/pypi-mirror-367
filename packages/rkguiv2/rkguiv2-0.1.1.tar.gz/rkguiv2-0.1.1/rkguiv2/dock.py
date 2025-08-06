import tkinter as tk

class Dock(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent.tk if hasattr(parent, "tk") else parent)
        self.pack(fill="both", expand=True)
        # TODO: реализовать док-панели и перетаскивание
