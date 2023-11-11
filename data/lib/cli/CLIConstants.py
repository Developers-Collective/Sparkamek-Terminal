#----------------------------------------------------------------------

    # Libraries
from data.lib.utils.Color import Color
from data.lib.LogType import LogType
#----------------------------------------------------------------------

    # Class
class CLIConstants:
    def __new__(cls) -> None: return None

    SpaceAlign = 2
    SpaceArgsAlign = 32 - SpaceAlign
    SpaceCommentAlign = 56 - SpaceArgsAlign - SpaceAlign

    MandatoryColor = Color.from_hex('#FF7FB6')
    OptionalColor = Color.from_hex('#A17FFF')

    ErrorColor = LogType.Error.value
    WarningColor = LogType.Warning.value
    SuccessColor = LogType.Success.value
    InfoColor = LogType.Info.value

    MagentaColor = Color.from_hex('#B4009E')
    BlueColor = Color.from_hex('#0094FF')
    CyanColor = Color.from_hex('#00B4FF')
    GreenColor = Color.from_hex('#16C60C')
    YellowColor = Color.from_hex('#FFD800')
    GrayColor = Color.from_hex('#767676')
    WhiteColor = Color.from_hex('#F2F2F2')
    Reset = Color.terminal_reset

    NeutralColor = Color.from_hex('#AAAAAA')
    BracketColor = Color.from_hex('#DDDDDD')
#----------------------------------------------------------------------
