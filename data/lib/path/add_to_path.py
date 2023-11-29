#----------------------------------------------------------------------

    # Libraries
import os, json, re
from ..PlatformType import PlatformType
from ..view import AddToPathWindow, AddToPathResponse
from ..GlobalValues import GlobalValues
from .apply_path import apply_path
from ..main_functions import format_msg, press_any_key, clear
from ..LogType import LogType
#----------------------------------------------------------------------

    # Function
def add_to_path() -> None:
    def save_config() -> None:
        with open('./config.json', 'w', encoding = 'utf8') as f:
            json.dump(config, f, indent = 4)

    with open('./config.json', 'r', encoding = 'utf8') as f:
        config = json.load(f)

    if not config['global'].get('addToPath'):
        config['global']['addToPath'] = {}
        save_config()

    user = os.getlogin()
    cwd = os.getcwd()

    if not config['global']['addToPath'].get(user, True): return

    match GlobalValues.platform:
        case PlatformType.Windows:
            import winreg

            current_user = winreg.HKEY_CURRENT_USER
            reg_path = winreg.OpenKey(current_user, r'Environment')

            user_path = list(winreg.QueryValueEx(reg_path, 'Path'))
            path_values = [p for p in user_path[0].split(';') if p != '']
            winreg.CloseKey(reg_path)


        case PlatformType.Linux:
            with open(f'{os.path.expanduser("~")}/.bashrc', 'r', encoding = 'utf8') as f:
                text = f.read()

            pattern = re.compile(r'export PATH[ \t\n]*=[ \t\n]*"([^"]*)"')
            path_values = []

            if path_result := pattern.search(text):
                path_values = text[path_result.start(1):path_result.end(1)].split(':')


        case PlatformType.MacOS:
            with open(f'{os.path.expanduser("~")}/.bash_profile', 'r', encoding = 'utf8') as f:
                text = f.read()

            pattern = re.compile(r'export PATH[ \t\n]*=[ \t\n]*"([^"]*)"')
            path_values = []

            if path_result := pattern.search(text):
                path_values = text[path_result.start(1):path_result.end(1)].split(':')


        case _:
            return


    if cwd in path_values:
        config['global']['addToPath'][user] = False
        save_config()
        return

    app = AddToPathWindow(platform = GlobalValues.platform, cwd = cwd)
    ret = app.run()

    match ret:
        case AddToPathResponse.Yes:
            try: apply_path(path_values, cwd)
            except Exception as e:
                print(format_msg(f'Unable to add to path: {e}', LogType.Error))
                press_any_key()
                clear()

            return

        case AddToPathResponse.No:
            return

        case AddToPathResponse.NoAndDontAskAgain:
            config['global']['addToPath'][user] = False
            save_config()
            return
#----------------------------------------------------------------------
