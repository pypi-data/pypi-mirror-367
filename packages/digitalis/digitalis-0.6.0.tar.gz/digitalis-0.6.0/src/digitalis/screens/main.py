import logging
import shlex
from collections.abc import Callable
from functools import partial
from pathlib import Path
from typing import ClassVar

from textual import events, on
from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.command import Hit, Hits, Provider
from textual.constants import MAX_FPS
from textual.containers import Horizontal, Vertical, HorizontalGroup
from textual.messages import ExitApp
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import (
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Static,
    TextArea,
    Button,
)

from digitalis.reader import create_source
from digitalis.reader.source import PlaybackSource
from digitalis.reader.types import MessageEvent, SourceInfo, Topic
from digitalis.screens.data import DataScreen
from digitalis.ui.datapanel import DataView
from digitalis.ui.search import TopicSearch
from digitalis.ui.timecontrol import TimeControl
from digitalis.utilities import get_file_paths


class MainScreen(Screen):
    DEFAULT_CSS = """
    MainScreen {
        align: center middle;
        padding: 0;
    }

    #title {
        width: auto;
    }
    #recent-files {
        padding: 2 2;
        Input {
            padding: 0 0;
            width: 1fr;
            margin: 0 0 5 0;
        }
    }
    .center {
        text-align: center;
    }
"""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(
            r"""  ____  _       _ _        _ _
 |  _ \(_) __ _(_) |_ __ _| (_)___
 | | | | |/ _` | | __/ _` | | / __|
 | |_| | | (_| | | || (_| | | \__ \
 |____/|_|\__, |_|\__\__,_|_|_|___/
          |___/""",
            id="title",
        )
        with Vertical(id="recent-files"):
            with HorizontalGroup():
                yield Input(
                    placeholder="Path or url to open",
                    id="topic-search",
                    classes="search",
                )
                yield Button(
                    "Open",
                    id="open-button",
                    variant="primary",
                    classes="search",
                )
            yield Static("[b]Recently Opened Files[/b]", classes="center")
            yield ListView(
                ListItem(Label("[b]ws://somewebsocket:8765[/b]\n2023-10-01")),
                ListItem(Label("Two\n2023-10-02")),
                ListItem(Label("Three\n2023-10-03")),
            )

    def on_paste(self, event: events.Paste) -> None:
        """Handle paste events to return to the previous screen."""
        for path in get_file_paths(event.text):
            if path.suffix == ".mcap":
                self.app.push_screen(DataScreen(str(path)))
                return
