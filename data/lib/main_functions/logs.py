#----------------------------------------------------------------------

    # Libraries
from ..LogType import LogType
from .format_msg import format_msg
from ..GlobalValues import GlobalValues
#----------------------------------------------------------------------

    # Functions
def log_simple(msg: str, log_type: LogType, invisible: bool = False) -> None:
    if GlobalValues.simple_logs: print(format_msg(msg, log_type, invisible).replace('&nbsp;', ' '))

def log_complete(msg: str, log_type: LogType, invisible: bool = False) -> None:
    print(format_msg(msg, log_type, invisible).replace('&nbsp;', ' '))
#----------------------------------------------------------------------
