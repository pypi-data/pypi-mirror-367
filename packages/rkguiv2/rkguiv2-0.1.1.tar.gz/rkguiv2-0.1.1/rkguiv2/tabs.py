import tkinter as tk
from tkinter import ttk

class Tabs(ttk.Notebook):
    def __init__(self, parent):
        super().__init__(parent.tk if hasattr(parent, "tk") else parent)
        self.pack(fill="both", expand=True)

    def add_tab(self, widget, title: str):
        self.add(widget.tk if hasattr(widget, "tk") else widget, text=title)

    def select_tab(self, index: int):
        self.select(index)
