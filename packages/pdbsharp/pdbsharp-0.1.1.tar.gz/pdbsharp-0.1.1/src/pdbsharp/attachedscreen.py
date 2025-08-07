import json
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Header, Input

from .debuginputarea import DebugInputArea
from .debugresponsearea import DebugResponseArea
from .messages import MessageFromRepl

if TYPE_CHECKING:
    from .pdbsharp import Pdbsharp


class AttachedScreen(Screen):
    prompt: reactive[str] = reactive("", init=False)

    BINDINGS = [
        Binding("ctrl+d", "detach", "Detach from Process", priority=True),
    ]

    CSS_PATH = "attachedscreen.tcss"

    def compose(self) -> ComposeResult:
        self.app: Pdbsharp
        self.sub_title = f"{self.app.pdbmode.name} to pid {self.app._server_pid if self.app._server_pid else '*unknown*'}"

        yield Header()
        with Vertical():
            yield DebugResponseArea()
            yield DebugInputArea().data_bind(AttachedScreen.prompt)
        yield Footer()

    def on_message_from_repl(self, message: MessageFromRepl):
        self.app: Pdbsharp
        payload: dict[str, str] = json.loads(message.text)
        match payload:
            case {"type": "pdbsharp", "message": msg}:
                self.screen.query_one(DebugResponseArea).write(f"{self.prompt}{msg}")
            case {"type": "info", "message": msg}:
                self.screen.query_one(DebugResponseArea).write(msg)
            case {"type": "error", "message": msg}:
                self.screen.query_one(DebugResponseArea).write("ERROR FROM PDB: " + msg)
            case {"command_list": _command_list}:
                self.app.command_list = _command_list[:]
            case {"state": state, "prompt": prompt}:
                self.prompt = prompt
            case _:
                raise ValueError(
                    f"Could not determine how to handle message from remote pdb: {payload}"
                )

    def on_screen_resume(self, *args):
        self.query_one(DebugInputArea).query_one(Input).focus()

    def action_detach(self):
        self.app: Pdbsharp
        self.app.detach()
