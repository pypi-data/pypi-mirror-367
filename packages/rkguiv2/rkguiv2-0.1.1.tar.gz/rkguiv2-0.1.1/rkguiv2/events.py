from __future__ import annotations
from collections import defaultdict
from typing import Callable, Any

class _Signal:
    def __init__(self):
        self._subs = defaultdict(list)

    def connect(self, name: str, fn: Callable[..., Any]):
        self._subs[name].append(fn)

    def disconnect(self, name: str, fn: Callable[..., Any]):
        if name in self._subs and fn in self._subs[name]:
            self._subs[name].remove(fn)

    def emit(self, name: str, *args, **kwargs):
        for fn in list(self._subs.get(name, [])):
            fn(*args, **kwargs)

signal = _Signal()
