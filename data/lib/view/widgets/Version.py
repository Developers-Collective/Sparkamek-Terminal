#----------------------------------------------------------------------

    # Libraries
from data.lib.version import VERSION_BUILD
from textual.widgets import Static
from rich.console import RenderableType
#----------------------------------------------------------------------

    # Class
class Version(Static):
    def render(self) -> RenderableType:
        return f'[b]{VERSION_BUILD[0]}\n{VERSION_BUILD[1]}[/b]'
#----------------------------------------------------------------------
