from __future__ import annotations
import tkinter as tk

class Widget:
    """Базовый класс: общий API для всех виджетов библиотеки."""
    def __init__(self, parent, **style):
        self.parent = parent
        self._style = style
        self._w = None  # реальный tk-виджет

    @property
    def tk(self) -> tk.Widget:
        return self._w

    def apply_style(self):
        if not self._w: 
            return
        if "bg" in self._style:
            self._w.configure(bg=self._style["bg"])
        if "fg" in self._style and hasattr(self._w, "configure"):
            try:
                self._w.configure(fg=self._style["fg"])
            except tk.TclError:
                pass
        if "font" in self._style:
            self._w.configure(font=self._style["font"])

    def pack(self, **kwargs):
        self._w.pack(**kwargs)
        return self

    def grid(self, **kwargs):
        self._w.grid(**kwargs)
        return self

    def place(self, **kwargs):
        self._w.place(**kwargs)
        return self
