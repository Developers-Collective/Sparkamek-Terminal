#----------------------------------------------------------------------

    # Libraries
import os, sys
OLD_PATH = os.getcwd()
os.chdir(os.path.dirname(os.path.abspath(__file__ if sys.argv[0].endswith('.py') else sys.executable)))

import json
from enum import StrEnum, Enum
from textual import *
from data.lib.CompilerWorker import CompilerWorker
from data.lib.LogType import LogType
from data.lib.view import *
from data.lib.cli import *
from data.lib.utils.Color import Color
from data.lib.version import VERSION
from data.lib.cliviews import *
#----------------------------------------------------------------------

    # Setup
simple_logs: bool = False
#----------------------------------------------------------------------

    # Functions
def format_msg(msg: str, log_type: LogType, invisible: bool = False) -> str:
    l = log_type.name
    if invisible:
        l = f'{Color.terminal_reset}' + ' ' * (len(l) + 2) * 2 + f'{Color.terminal_reset}'

    def gen_span(msg: str, color: Color, background: bool = False) -> str:
        return f'{color.terminal_background if background else color.terminal_color}{msg}{Color.terminal_reset}'

    if invisible: return f'{l} {gen_span(msg, CLIConstants.NeutralColor)}'
    return f'{gen_span("[", CLIConstants.BracketColor)}{gen_span(l, log_type.value)}{gen_span("]", CLIConstants.BracketColor)} {gen_span(msg, CLIConstants.NeutralColor)}'

def log_simple(msg: str, log_type: LogType, invisible: bool = False) -> None:
    if simple_logs: print(format_msg(msg, log_type, invisible).replace('&nbsp;', ' '))

def log_complete(msg: str, log_type: LogType, invisible: bool = False) -> None:
    if not simple_logs: print(format_msg(msg, log_type, invisible).replace('&nbsp;', ' '))

def press_any_key(time: int = -1) -> None:
    if time < 0: os.system('bash -c \'read -s -n 1 -p "Press any key to continue..."\'')
    else: os.system(f'bash -c \'read -s -t {time} -n 1 -p "Press any key to continue..."\'')

def clear() -> None:
    os.system('clear')
#----------------------------------------------------------------------

    # Main
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



def main():
    config, devkitppc_path = load_config()

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

        try: compile(project, devkitppc_path)
        except FileNotFoundError: break



def parse_cli(config_file: CommandResult, add_project: CommandResult = None) -> None:
    config, devkitppc_path = load_config()

    path = os.getcwd()
    os.chdir(OLD_PATH)

    if not os.path.isfile(config_file.path):
        print(format_msg('Unable to find the config file. Please make sure it exists at the given path.', LogType.Error))
        press_any_key()
        return

    with open(config_file.path, 'r', encoding = 'utf8') as f:
        project = json.load(f)
        try: project['path'] = os.path.abspath(project['path'])
        except Exception:
            print(format_msg('Unable to find the project path. Please make sure it exists at the given path.', LogType.Error))
            press_any_key()
            return

    os.chdir(path)

    if add_project is not None:
        existing_projects = [p['name'] for p in config['projects']]
        if project['name'] not in existing_projects:
            with open('./config.json', 'w', encoding = 'utf8') as f:
                config['projects'].append(project)
                json.dump(config, f, indent = 4)
            print(format_msg(f'Added project {project["name"]} to config.json', LogType.Success))
            press_any_key(3)

        else:
            index = existing_projects.index(project['name'])
            old_project = config['projects'][index]
            if old_project != project:
                with open('./config.json', 'w', encoding = 'utf8') as f:
                    config['projects'][index] = project
                    json.dump(config, f, indent = 4)
                print(format_msg(f'Updated project {project["name"]} in config.json', LogType.Success))
                press_any_key(3)

    compile(project, devkitppc_path)



def compile(project: dict, devkitppc_path: str) -> None:
    global simple_logs

    simple_logs = project['simpleLogs']

    if not os.path.exists(project['path']):
        print(format_msg(f'Unable to find path for project {project["name"]}', LogType.Error))
        press_any_key()
        clear()
        raise FileNotFoundError()

    clear()

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
    if len(sys.argv) > 1:
        mainview(__file__ if sys.argv[0].endswith('.py') else sys.executable, parse_cli)
    else: main()
#----------------------------------------------------------------------
