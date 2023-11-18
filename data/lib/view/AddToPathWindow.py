#----------------------------------------------------------------------

    # Libraries
from data.lib.version import VERSION
from data.lib.PlatformType import PlatformType
from .AddToPathWindowData.AddToPathResponse import AddToPathResponse
from textual._path import CSSPathType
from textual.app import App, CSSPathType, ComposeResult
from textual.driver import Driver
from textual.widgets import Button, Footer, Header, Button, Label
from textual.containers import Container
from textual.binding import Binding
from textual import on
from textual.reactive import reactive
import webbrowser
from .widgets import Sidebar, Body
#----------------------------------------------------------------------

    # Class
class AddToPathWindow(App):
    CSS_PATH = 'sparkamek.tcss'

    BINDINGS = [
        Binding(key = 'ctrl+q', action = 'quit', description = 'Exit', key_display = 'Ctrl+Q'),
        Binding(key = 'f1', action = 'help', description = 'Help', key_display = 'F1'),
    ]

    show_sidebar = reactive(False)


    def __init__(self, driver_class: type[Driver] | None = None, css_path: CSSPathType | None = None, watch_css: bool = False, platform: PlatformType = PlatformType.Windows, cwd: str = '') -> None:
        super().__init__(driver_class, css_path, watch_css)
        self._platform = platform
        self._cwd = cwd

        self.title = f'Sparkamek Terminal | {VERSION[0]} • {VERSION[1]} > Add to Path'
        self._buttons = []


    def compose(self) -> ComposeResult:
        with Container(id = 'root'):
            yield Sidebar(classes = '-hidden')
            yield Header()

            with Body():
                yield Label('💡 [i]You can use your mouse on this screen.[/]\n\n', classes = 'italic')
                yield Label('[b]It looks like Sparkamek Terminal is not in your PATH environment variable.\nWould you like to add it now ?[/]\n', id = 'title')

                with Container(id = 'vertical-buttons'):
                    for choice in AddToPathResponse:
                        b = Button(choice.value[0], id = choice.value[1], variant = 'primary' if choice == AddToPathResponse.Yes else 'default', classes = 'choice')
                        self._buttons.append(b)
                        yield b

        yield Footer()


    @on(Button.Pressed, '.choice')
    def on_choice(self, event: Button.Pressed) -> None:
        self.exit(AddToPathResponse.from_str(event.button.id))


    def action_help(self) -> None:
        sidebar = self.query_one(Sidebar)

        if sidebar.has_class('-hidden'):
            sidebar.remove_class('-hidden')
            self.set_focus(None)

        else:
            if sidebar.query('*:focus'): self.screen.set_focus(None)
            sidebar.add_class('-hidden')
            self.set_focus(self._buttons[0])

    def action_open_link(self, link: str) -> None:
        webbrowser.open(link)
#----------------------------------------------------------------------
