#----------------------------------------------------------------------

    # Libraries
import sys
from .PlatformType import PlatformType
#----------------------------------------------------------------------

    # Class
class GlobalValues:
    def __new__(cls) -> None:
        return None
    
    simple_logs: bool = False
    platform = PlatformType.from_str(sys.platform)
    old_path: str = ''
#----------------------------------------------------------------------
