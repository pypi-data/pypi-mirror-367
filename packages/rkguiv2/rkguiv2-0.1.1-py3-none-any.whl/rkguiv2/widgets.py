from __future__ import annotations
import tkinter as tk
from .core import Widget

class Label(Widget):
    def __init__(self, parent, text: str = "", **style):
        super().__init__(parent, **style)
        self._w = tk.Label(parent.tk if hasattr(parent, "tk") else parent, text=text)
        self.apply_style()

class Button(Widget):
    def __init__(self, parent, text: str = "Button", on_click=None, **style):
        super().__init__(parent, **style)
        self._w = tk.Button(parent.tk if hasattr(parent, "tk") else parent, text=text, command=on_click)
        self.apply_style()

class Entry(Widget):
    def __init__(self, parent, **style):
        super().__init__(parent, **style)
        self.var = tk.StringVar()
        self._w = tk.Entry(parent.tk if hasattr(parent, "tk") else parent, textvariable=self.var)
        self.apply_style()

    def text(self) -> str:
        return self.var.get()

    def set_text(self, value: str):
        self.var.set(value)

class ScrollArea(Widget):
    def __init__(self, parent, **style):
        super().__init__(parent, **style)
        root = parent.tk if hasattr(parent, "tk") else parent
        outer = tk.Frame(root)
        canvas = tk.Canvas(outer, highlightthickness=0)
        vbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vbar.set)
        inner = tk.Frame(canvas)

        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")

        self._outer, self._canvas, self._inner, self._vbar = outer, canvas, inner, vbar
        self._w = outer
        canvas.pack(side="left", fill="both", expand=True)
        vbar.pack(side="right", fill="y")
        self.apply_style()

    @property
    def content(self) -> tk.Frame:
        return self._inner
