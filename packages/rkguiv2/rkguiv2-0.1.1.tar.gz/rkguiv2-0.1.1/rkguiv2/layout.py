from __future__ import annotations
import tkinter as tk
from .core import Widget

class _Box(Widget):
    def __init__(self, parent, orient="vertical", spacing=6, padding=8, **style):
        super().__init__(parent, **style)
        self._w = tk.Frame(parent.tk if hasattr(parent, "tk") else parent)
        self.orient = orient
        self.spacing = spacing
        self.padding = padding
        self.apply_style()
        self._w.configure(padx=padding, pady=padding)

    def add(self, child: Widget, **pack):
        if self.orient == "vertical":
            pack.setdefault("side", "top")
        else:
            pack.setdefault("side", "left")
        if self.spacing:
            pack.setdefault("padx", self.spacing if self.orient == "horizontal" else 0)
            pack.setdefault("pady", self.spacing if self.orient == "vertical" else 0)
        child.pack(in_=self._w, **pack)
        return child

class VBox(_Box):
    def __init__(self, parent, **style):
        super().__init__(parent, orient="vertical", **style)

class HBox(_Box):
    def __init__(self, parent, **style):
        super().__init__(parent, orient="horizontal", **style)

class Grid(tk.Frame):
    def __init__(self, parent, rows=1, columns=1, **kwargs):
        super().__init__(parent.tk if hasattr(parent, "tk") else parent, **kwargs)
        self.rows = rows
        self.columns = columns
        self.pack(fill="both", expand=True)

    def add(self, widget, row, column, rowspan=1, columnspan=1, **grid_opts):
        widget.pack_forget()
        widget.tk.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, **grid_opts)
