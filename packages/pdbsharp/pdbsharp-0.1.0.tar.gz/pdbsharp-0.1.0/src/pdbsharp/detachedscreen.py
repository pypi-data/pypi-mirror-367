from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Header, Input

if TYPE_CHECKING:
    from .pdbsharp import Pdbsharp


class DetachedScreen(Screen):
    def compose(self) -> ComposeResult:
        self.app: Pdbsharp
        yield Header()
        self.sub_title = f"{self.app.pdbmode.name}"

        yield Input("", placeholder="Remote Process PID", type="integer")
        yield Footer()
