from tkinter import filedialog

class FileDialog:
    @staticmethod
    def open_file(**options):
        return filedialog.askopenfilename(**options)

    @staticmethod
    def save_file(**options):
        return filedialog.asksaveasfilename(**options)

    @staticmethod
    def select_folder(**options):
        return filedialog.askdirectory(**options)
