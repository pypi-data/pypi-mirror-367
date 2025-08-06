import tkinter as tk
from tkinter import simpledialog, messagebox

class Dialog:
    @staticmethod
    def alert(title: str, message: str):
        messagebox.showinfo(title, message)

    @staticmethod
    def confirm(title: str, message: str) -> bool:
        return messagebox.askyesno(title, message)

    @staticmethod
    def prompt(title: str, prompt: str) -> str | None:
        return simpledialog.askstring(title, prompt)
