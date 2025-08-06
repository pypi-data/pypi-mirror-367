import tkinter as tk

class StatusBar(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent.tk if hasattr(parent, "tk") else parent)
        self.label = tk.Label(self, bd=1, relief=tk.SUNKEN, anchor="w")
        self.label.pack(fill="x")
        self.pack(side="bottom", fill="x")

    def set_text(self, text: str):
        self.label.config(text=text)
