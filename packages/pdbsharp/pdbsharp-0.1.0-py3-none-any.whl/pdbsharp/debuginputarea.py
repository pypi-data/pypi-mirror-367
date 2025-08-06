from typing import TYPE_CHECKING

from textual.message import Message
from textual.widgets import Input, TextArea

from .pdbstate import PdbMessageType

if TYPE_CHECKING:
    from .pdbsharp import Pdbsharp


class DebugInputArea(Input):
    BINDINGS = [
        ("ctrl+c", "interrupt", "Send Ctrl+C"),
        ("ctrl+d", "detach", "Detach from Process"),
    ]

    class ReplMessage(Message):
        def __init__(self, type: PdbMessageType, content: str | None = None) -> None:
            self.type = type
            self.content = content
            super().__init__()

    def action_submit(self):
        self.post_message(
            self.ReplMessage(type=PdbMessageType.COMMAND, content=self.value)
        )
        self.value = ""

    def action_interrupt(self):
        self.post_message(self.ReplMessage(type=PdbMessageType.INT))
        self.value = ""

    def action_detach(self):
        self.app: Pdbsharp
        self.app.detach()
