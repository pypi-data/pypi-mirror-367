from typing import TYPE_CHECKING

from textual.widgets import Log

if TYPE_CHECKING:
    from .pdbsharp import Pdbsharp


class DebugResponseArea(Log):
    def write(self, obj):
        self.write_line(str(obj))

    def clear(self):
        super().clear()
