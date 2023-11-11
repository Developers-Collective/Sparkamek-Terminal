#----------------------------------------------------------------------

    # Libraries
from enum import Enum
from data.lib.utils.Color import Color
#----------------------------------------------------------------------

    # Class
class LogType(Enum):
    Error = Color.from_hex('#E74856')
    Warning = Color.from_hex('#F9F1A5')
    Success = Color.from_hex('#16C60C')
    Info = Color.from_hex('#61D6D6')
#----------------------------------------------------------------------
