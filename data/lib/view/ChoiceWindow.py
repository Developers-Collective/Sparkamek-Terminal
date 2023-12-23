#----------------------------------------------------------------------

    # Libraries
from data.lib.version import VERSION_BUILD
from textual._path import CSSPathType
from textual.app import App, CSSPathType, ComposeResult
from textual.driver import Driver
from textual.widgets import Button, Footer, Header, OptionList, Button, Label, Static, RichLog
from textual.widgets.option_list import Option
from textual.containers import Container, ScrollableContainer
from textual.binding import Binding
from textual import on, events
from textual.css.query import NoMatches
from textual.reactive import reactive
from rich.console import RenderableType
import webbrowser
from .widgets import Sidebar, Body
#----------------------------------------------------------------------

    # Class
class ChoiceWindow(App):
    CSS_PATH = 'sparkamek.tcss'

    BINDINGS = [
        Binding(key = 'ctrl+q', action = 'quit', description = 'Exit', key_display = 'Ctrl+Q'),
        Binding(key = 'none', action = 'compile', description = 'Compile Selected Project', key_display = 'Enter'),
        Binding(key = 'f1', action = 'help', description = 'Help', key_display = 'F1'),
    ]

    show_sidebar = reactive(False)


    def add_note(self, renderable: RenderableType) -> None:
        self.query_one(RichLog).write(renderable)


    def __init__(self, driver_class: type[Driver] | None = None, css_path: CSSPathType | None = None, watch_css: bool = False, projects: list[str] = [], selected_id: int = 0):
        super().__init__(driver_class, css_path, watch_css)
        self._projects = projects
        self._selected_id = selected_id
        self._list = None

        self.title = f'Sparkamek Terminal | {VERSION_BUILD[0]} • {VERSION_BUILD[1]}'


    def compose(self) -> ComposeResult:
        with Container(id = 'root'):
            yield Sidebar(classes = '-hidden')
            yield Header()

            with Body():
                yield Label('💡 [i]You can use your mouse on this screen.[/]\n\n', classes = 'italic')
                yield Label('[b]Select a project to compile:[/]\n', id = 'title')

                with Container(id = 'list'):
                    self._list = OptionList(
                        *[Option(f' {project}', id = i) for i, project in enumerate(self._projects)],
                        id = 'projects'
                    )
                    for _ in range(self._selected_id): self._list.action_cursor_down()
                    yield self._list

                with Container(id = 'buttons'):
                    yield Button('Exit', variant = 'default', id = 'exit')
                    yield Button('Compile', variant = 'primary', id = 'compile')

        yield Footer()


    def on_key(self, event: events.Key) -> None:
        try:
            if event.key == 'enter': self._compile(None)
        except NoMatches: pass


    @on(OptionList.OptionSelected, '#projects')
    def _select_project(self, event: OptionList.OptionSelected) -> None:
        self._selected_id = event.option.id


    @on(OptionList.OptionHighlighted, '#projects')
    def _select_project(self, event: OptionList.OptionHighlighted) -> None:
        self._selected_id = event.option.id


    @on(Button.Pressed, '#compile')
    def _compile(self, event: Button.Pressed) -> None:
        self.exit(result = self._selected_id)


    def action_compile(self) -> None:
        self._compile(None)


    def action_help(self) -> None:
        sidebar = self.query_one(Sidebar)

        if sidebar.has_class('-hidden'):
            sidebar.remove_class('-hidden')
            self.set_focus(None)

        else:
            if sidebar.query('*:focus'): self.screen.set_focus(None)
            sidebar.add_class('-hidden')
            self.set_focus(self._list)


    def action_open_link(self, link: str) -> None:
        webbrowser.open(link)


    @on(Button.Pressed, '#exit')
    def _exit(self, event: Button.Pressed) -> None:
        self.exit()
#----------------------------------------------------------------------
