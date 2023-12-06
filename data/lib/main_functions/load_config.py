#----------------------------------------------------------------------

    # Libraries
import os, sys, json
from . import format_msg
from ..LogType import LogType
from .cmd import press_any_key
#----------------------------------------------------------------------

    # Function
def load_config() -> tuple[dict, str]:
    if not os.path.isfile('./config.json'):
        print(format_msg('Unable to find the config.json file. Please make sure it is in the same directory as this program.\nIf you don\'t have one yet, you can use the config-sample.json file as a template.', LogType.Error))
        press_any_key()
        sys.exit()

    with open('./config.json', 'r', encoding = 'utf8') as f:
        config: dict = json.load(f)

    global_config: dict = config['global']

    devkitppc_path: str = None
    match sys.platform:
        case 'win32':
            devkitppc_path = global_config['devkitPPCPath']['win32']

        case _:
            devkitppc_path = global_config['devkitPPCPath']['default']

    return config, devkitppc_path
#----------------------------------------------------------------------
