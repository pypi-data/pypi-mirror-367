from __future__ import annotations
import tkinter as tk
from .theme import Theme

class App:
    """Обёртка над Tk: единая точка запуска, тема, глобальные хуки."""
    def __init__(self, title: str = "MyGUI App", theme: Theme | None = None):
        self._root = tk.Tk()
        self._root.title(title)
        self.theme = theme or Theme()
        self.theme.apply(self._root)

        # DPI awareness / High-DPI (по возможности)
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

    @property
    def tk(self) -> tk.Tk:
        return self._root

    def run(self):
        self._root.mainloop()

    def quit(self):
        self._root.quit()
