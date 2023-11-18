#----------------------------------------------------------------------

    # Libraries
from data.lib.version import VERSION
from data.lib.PlatformType import PlatformType
from .AddToPathWindowData.AddToPathResponse import AddToPathResponse
from textual._path import CSSPathType
from textual.app import App, CSSPathType, ComposeResult
from textual.driver import Driver
from textual.widgets import Button, Footer, Header, Button, Label, Static, RadioSet, RadioButton
from textual.containers import Container, ScrollableContainer
from textual.binding import Binding
from textual import on
from rich.console import RenderableType
#----------------------------------------------------------------------

    # Class
class Body(ScrollableContainer): pass


class Title(Static): pass


class OptionGroup(Container): pass


class Message(Static): pass


class Version(Static):
    def render(self) -> RenderableType:
        return f'[b]{VERSION[0]}\n{VERSION[1]}[/b]'


class Column(Container): pass


class AddToPathWindow(App):
    CSS_PATH = 'sparkamek.tcss'

    BINDINGS = [
        Binding(key = 'ctrl+q', action = 'quit', description = 'Exit', key_display = 'Ctrl+Q'),
    ]

    def __init__(self, driver_class: type[Driver] | None = None, css_path: CSSPathType | None = None, watch_css: bool = False, platform: PlatformType = PlatformType.Windows, cwd: str = '') -> None:
        super().__init__(driver_class, css_path, watch_css)
        self._platform = platform
        self._cwd = cwd

        self.title = f'Sparkamek Terminal | {VERSION[0]} • {VERSION[1]} > Add to Path'

        self._current_choice: AddToPathResponse = AddToPathResponse.Yes

    def compose(self) -> ComposeResult:
        with Container(id = 'root'):
            yield Header()

            with Body():
                yield Label('💡 [i]You can use your mouse on this screen.[/]\n\n', classes = 'italic')
                yield Label('[b]It looks like Sparkamek Terminal is not in your PATH environment variable.\nWould you like to add it now ?[/]\n', id = 'title')

                with Container(id = 'choice'):
                    choices = [RadioButton(choice.value[0], id = choice.value[1], value = choice == AddToPathResponse.Yes) for choice in AddToPathResponse]
                    self._choices = RadioSet(
                        *choices,
                        id = 'choices'
                    )
                    yield self._choices

                with Container(id = 'buttons'):
                    yield Button('Submit', variant = 'primary', id = 'submit')

        yield Footer()

    @on(RadioSet.Changed, '#choices')
    def _choices_changed(self, event: RadioSet.Changed) -> None:
        self._current_choice = AddToPathResponse.from_str(event.pressed.id)

    @on(Button.Pressed, '#submit')
    def _submit(self, event: Button.Pressed) -> None:
        self.exit(result = self._current_choice)
#----------------------------------------------------------------------
