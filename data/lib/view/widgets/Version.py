#----------------------------------------------------------------------

    # Libraries
from data.lib.version import VERSION
from textual.widgets import Static
from rich.console import RenderableType
#----------------------------------------------------------------------

    # Class
class Version(Static):
    def render(self) -> RenderableType:
        return f'[b]{VERSION[0]}\n{VERSION[1]}[/b]'
#----------------------------------------------------------------------
