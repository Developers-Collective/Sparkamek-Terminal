#----------------------------------------------------------------------

    # Libraries
from textual.app import ComposeResult
from textual.containers import Container
from .Title import Title
from .OptionGroup import OptionGroup
from .Message import Message
from .Version import Version
#----------------------------------------------------------------------

    # Class
class Sidebar(Container):
    def compose(self) -> ComposeResult:
        yield Title('Help Menu')
        yield OptionGroup(
            Message(
            'I hope you enjoy using Sparkamek Terminal. Here are some useful links if case you need them.' + '\n\n' +
            '[@click="open_link(\'https://github.com/Synell/Sparkamek-Terminal#known-issues-question-mark-instead-of-special-characters\')"]Display Problem[/]' + '\n\n\n' +
            'Built with ♥ by [@click="open_link(\'https://github.com/Synell/\')"]Synel[/] with [@click="app.open_link(\'https://www.textualize.io\')"]Textualize.io[/]'
        ),
        Version()
    )
#----------------------------------------------------------------------
