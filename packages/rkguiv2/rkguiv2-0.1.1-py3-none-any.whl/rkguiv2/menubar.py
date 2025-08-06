import tkinter as tk

class MenuBar:
    def __init__(self, app):
        self._root = app.tk
        self.menu = tk.Menu(self._root)
        self._root.config(menu=self.menu)
        self._menus = {}

    def add_menu(self, label: str) -> tk.Menu:
        menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label=label, menu=menu)
        self._menus[label] = menu
        return menu

    def add_command(self, menu_label: str, label: str, command):
        if menu_label not in self._menus:
            self.add_menu(menu_label)
        self._menus[menu_label].add_command(label=label, command=command)

    def add_separator(self, menu_label: str):
        if menu_label in self._menus:
            self._menus[menu_label].add_separator()
