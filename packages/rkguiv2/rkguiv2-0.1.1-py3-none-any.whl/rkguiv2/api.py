from .events import signal

class API:
    def __init__(self):
        self.signal = signal
        self.theme = None

    def set_theme(self, theme):
        self.theme = theme

api = API()
