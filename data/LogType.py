#----------------------------------------------------------------------

    # Libraries
from enum import Enum
import colorama
#----------------------------------------------------------------------

    # Class
class LogType(Enum):
    Error = colorama.Back.LIGHTRED_EX + colorama.Fore.BLACK
    Warning = colorama.Back.LIGHTYELLOW_EX + colorama.Fore.BLACK
    Success = colorama.Back.LIGHTGREEN_EX + colorama.Fore.BLACK
    Info = colorama.Back.LIGHTCYAN_EX + colorama.Fore.BLACK

    @staticmethod
    def to_fore(logtype: 'LogType') -> colorama.Fore:
        match logtype:
            case LogType.Error: return colorama.Fore.LIGHTRED_EX
            case LogType.Warning: return colorama.Fore.LIGHTYELLOW_EX
            case LogType.Success: return colorama.Fore.LIGHTGREEN_EX
            case LogType.Info: return colorama.Fore.LIGHTCYAN_EX
#----------------------------------------------------------------------
