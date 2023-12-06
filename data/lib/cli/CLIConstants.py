#----------------------------------------------------------------------

    # Libraries
from data.lib.utils.Color import Color
from data.lib.LogType import LogType
#----------------------------------------------------------------------

    # Class
class CLIConstants:
    def __new__(cls) -> None: return None

    # SpaceAlign = 2
    # SpaceArgsAlign = 32 - SpaceAlign
    # SpaceCommentAlign = 56 - SpaceArgsAlign - SpaceAlign
    SpaceOffset = 2
    SpaceSeparator = 4

    MandatoryColor = Color.from_hex('#33D472')
    OptionalColor = Color.from_hex('#33C7DE')

    ErrorLogColor = LogType.Error.value
    WarningLogColor = LogType.Warning.value
    SuccessLogColor = LogType.Success.value
    InfoLogColor = LogType.Info.value

    TitleColor = Color.from_hex('#0094FF')
    MagentaColor = Color.from_hex('#B4009E')
    VersionTitleColor = Color.from_hex('#00B4FF')
    VersionDigitColor = Color.from_hex('#16C60C')
    CommandColor = Color.from_hex('#FFD800')
    ErrorColor = Color.from_hex('#FF3232')
    VersionSeparatorColor = Color.from_hex('#767676')
    FontColor = Color.from_hex('#F2F2F2')
    Reset = Color.terminal_reset

    NeutralColor = Color.from_hex('#DDD')
    BracketColor = Color.from_hex('#777')
#----------------------------------------------------------------------
