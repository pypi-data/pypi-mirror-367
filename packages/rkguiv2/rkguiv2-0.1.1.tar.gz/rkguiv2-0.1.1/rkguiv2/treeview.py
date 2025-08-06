import tkinter as tk
from tkinter import ttk

class TreeView(ttk.Treeview):
    def __init__(self, parent):
        super().__init__(parent.tk if hasattr(parent, "tk") else parent)
        self.pack(fill="both", expand=True)

    def insert_item(self, parent_item, text: str, iid=None, open=False):
        return self.insert(parent_item, "end", iid=iid, text=text, open=open)

    def clear(self):
        for i in self.get_children():
            self.delete(i)
