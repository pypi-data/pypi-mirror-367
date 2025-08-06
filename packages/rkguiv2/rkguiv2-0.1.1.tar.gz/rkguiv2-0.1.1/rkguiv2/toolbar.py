import tkinter as tk

class ToolBar(tk.Frame):
    def __init__(self, parent, **style):
        super().__init__(parent.tk if hasattr(parent, "tk") else parent, **style)
        self.pack(side="top", fill="x")
        self.buttons = []

    def add_button(self, text: str, command=None):
        btn = tk.Button(self, text=text, command=command)
        btn.pack(side="left", padx=2, pady=2)
        self.buttons.append(btn)
        return btn
