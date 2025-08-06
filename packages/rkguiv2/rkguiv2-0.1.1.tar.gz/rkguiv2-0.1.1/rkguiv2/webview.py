import tkinter as tk
try:
    import webview
except ImportError:
    webview = None

class WebView(tk.Frame):
    def __init__(self, parent, url: str = "https://www.google.com"):
        super().__init__(parent.tk if hasattr(parent, "tk") else parent)
        self.pack(fill="both", expand=True)
        if webview is None:
            label = tk.Label(self, text="pywebview not installed")
            label.pack()
            return
        self.window = webview.create_window("WebView", url=url, gui='tkinter', debug=False)
        import threading
        threading.Thread(target=webview.start, daemon=True).start()
