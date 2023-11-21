#----------------------------------------------------------------------

    # Libraries
from enum import Enum
#----------------------------------------------------------------------

    # Class
class PlatformType(Enum):
    Windows = ['windows-64', 'windows-32', 'win-64', 'win-32', 'win64', 'win32', 'win32-64', 'win64-32', 'windows', 'win', '.exe']
    Linux = ['linux', 'ubuntu', 'debian', 'fedora', 'arch']
    MacOS = ['macos', 'mac']

    @staticmethod
    def from_str(platform: str) -> 'PlatformType':
        match platform:
            case 'win32': return PlatformType.Windows
            case 'linux': return PlatformType.Linux
            case 'darwin': return PlatformType.MacOS
            case _: raise ValueError(f'Unknown platform: {platform}')
#----------------------------------------------------------------------
