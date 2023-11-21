#----------------------------------------------------------------------

    # Libraries
from ..LogType import LogType
from ..utils.Color import Color
from ..cli.CLIConstants import CLIConstants
#----------------------------------------------------------------------

    # Function
def format_msg(msg: str, log_type: LogType, invisible: bool = False) -> str:
    l = log_type.name
    if invisible:
        l = f'{Color.terminal_reset}' + ' ' * (len(l) + 2) * 2 + f'{Color.terminal_reset}'

    def gen_span(msg: str, color: Color, background: bool = False) -> str:
        return f'{color.terminal_background if background else color.terminal_color}{msg}{Color.terminal_reset}'

    if invisible: return f'{l} {gen_span(msg, CLIConstants.NeutralColor)}'
    return f'{gen_span("[", CLIConstants.BracketColor)}{gen_span(l, log_type.value)}{gen_span("]", CLIConstants.BracketColor)} {gen_span(msg, CLIConstants.NeutralColor)}'
#----------------------------------------------------------------------
