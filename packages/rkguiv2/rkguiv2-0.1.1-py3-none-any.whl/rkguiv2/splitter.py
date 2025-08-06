import tkinter as tk

class Splitter(tk.PanedWindow):
    def __init__(self, parent, orient="horizontal"):
        orient_const = tk.HORIZONTAL if orient == "horizontal" else tk.VERTICAL
        super().__init__(parent.tk if hasattr(parent, "tk") else parent, orient=orient_const)
        self.pack(fill="both", expand=True)

    def add_pane(self, widget):
        self.add(widget.tk if hasattr(widget, "tk") else widget)
