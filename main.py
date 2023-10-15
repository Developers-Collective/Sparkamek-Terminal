#----------------------------------------------------------------------

    # Libraries
import os, colorama, json, sys
from textual import *
from data.CompilerWorker import CompilerWorker
from data.LogType import LogType
from data.view import *
#----------------------------------------------------------------------

    # Setup
os.chdir(os.path.dirname(os.path.abspath(__file__ if sys.argv[0].endswith('.py') else sys.executable)))
colorama.init(autoreset = True)

neutral_color = colorama.Fore.WHITE
bracket_color = colorama.Fore.LIGHTBLACK_EX
simple_logs: bool = False
#----------------------------------------------------------------------

    # Functions
def format_msg(msg: str, log_type: LogType, invisible: bool = False) -> str:
    l = log_type.name
    if invisible:
        l = f'{colorama.Style.RESET_ALL}' + ' ' * (len(l) + 2) * 2 + f'{colorama.Style.RESET_ALL}'

    def gen_span(msg: str, color: colorama.Fore) -> str:
        return f'{color}{msg}{colorama.Style.RESET_ALL}'

    if invisible: return f'{l} {gen_span(msg, neutral_color)}'
    return f'{gen_span("[", bracket_color)}{gen_span(l, LogType.to_fore(log_type))}{gen_span("]", bracket_color)} {gen_span(msg, neutral_color)}'

def log_simple(msg: str, log_type: LogType, invisible: bool = False) -> None:
    if simple_logs: print(format_msg(msg, log_type, invisible).replace('&nbsp;', ' '))

def log_complete(msg: str, log_type: LogType, invisible: bool = False) -> None:
    if not simple_logs: print(format_msg(msg, log_type, invisible).replace('&nbsp;', ' '))

def press_any_key() -> None:
    os.system('bash -c \'read -s -n 1 -p "Press any key to continue..."\'')

def clear() -> None:
    os.system('clear')
#----------------------------------------------------------------------

    # Main
def main():
    global simple_logs

    if not os.path.isfile('./config.json'):
        print(format_msg('Unable to find the config.json file. Please make sure it is in the same directory as this program.\nIf you don\'t have one yet, you can use the config-sample.json file as a template.', LogType.Error))
        press_any_key()
        return

    with open('./config.json', 'r', encoding = 'utf8') as f:
        config: dict = json.load(f)

    global_config: dict = config['global']

    devkitppc_path: str = None
    match sys.platform:
        case 'win32':
            devkitppc_path = global_config['devkitPPCPath']['win32']

        case _:
            devkitppc_path = global_config['devkitPPCPath']['default']

    if not (devkitppc_path is not None and os.path.isdir(devkitppc_path)):
        print(format_msg('Unable to find devkitPPC path. Please set it manually in config.json', LogType.Error))
        press_any_key()
        return

    projects: list[dict] = config['projects']

    if len(projects) == 0:
        print(format_msg('No projects found in config.json', LogType.Error))
        press_any_key()
        return

    options = [f'{project["name"]}' for project in projects]

    selected_id = 0

    while True:
        app = ChoiceWindow(projects = options, selected_id = selected_id)
        selected_id = app.run()
        if selected_id is None: break
        clear()

        project = projects[selected_id]

        simple_logs = project['simpleLogs']

        if not os.path.exists(project['path']):
            print(format_msg(f'Unable to find path for project {project["name"]}', LogType.Error))
            press_any_key()
            clear()
            break

        worker = CompilerWorker(
            data = project,
            devkitppc_path = devkitppc_path
        )
        worker.log_simple.connect(log_simple)
        worker.log_complete.connect(log_complete)
        worker.run()

        press_any_key()
        clear()

if __name__ == '__main__':
    main()
#----------------------------------------------------------------------
