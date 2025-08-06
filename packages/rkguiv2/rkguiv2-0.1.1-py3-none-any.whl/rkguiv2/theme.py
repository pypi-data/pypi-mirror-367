from __future__ import annotations
import tkinter as tk
from tkinter import ttk

class Theme:
    """Мини-тема: шрифты/цвета/ttk-стиль."""
    def __init__(self, family="Segoe UI", size=10, bg="#202124", fg="#E8EAED"):
        self.family = family
        self.size = size
        self.bg = bg
        self.fg = fg

    def apply(self, root: tk.Tk):
        root.configure(bg=self.bg)
        default_font = (self.family, self.size)
        root.option_add("*Font", default_font)
        root.option_add("*Background", self.bg)
        root.option_add("*Foreground", self.fg)

        style = ttk.Style(root)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure(".", background=self.bg, foreground=self.fg, fieldbackground=self.bg)
        style.map("TButton", foreground=[("disabled", "#777")])
