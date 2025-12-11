import sys
from types import ModuleType


class ReadlineStub(ModuleType):
    def __init__(self):
        super().__init__("readline")
        self.reset()

    def reset(self, doc="readline stub", delims=" \t\n/"):
        self.__doc__ = doc
        self._delims = delims
        self._completer = None
        self.last_bindings = []

    def set_completer(self, completer):
        self._completer = completer

    def get_completer_delims(self):
        return self._delims

    def set_completer_delims(self, delims):
        self._delims = delims

    def parse_and_bind(self, command):
        self.last_bindings.append(command)


readline_stub = ReadlineStub()
sys.modules["readline"] = readline_stub
