from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Footer, Header

from .debuginputarea import DebugInputArea
from .debugresponsearea import DebugResponseArea

if TYPE_CHECKING:
    from .pdbsharp import Pdbsharp


class AttachedScreen(Screen):
    class MessageFromRepl(Message):
        def __init__(self, text):
            self.text = text
            super().__init__()

    def compose(self) -> ComposeResult:
        self.app: Pdbsharp
        self.sub_title = f"{self.app.pdbmode.name} to pid {self.app._server_pid if self.app._server_pid else '*unknown*'}"
        yield Header()
        yield DebugResponseArea()
        yield DebugInputArea()
        yield Footer()

    def on_attached_screen_message_from_repl(
        self, message: AttachedScreen.MessageFromRepl
    ):
        self.query_one(DebugResponseArea).write(message.text)
