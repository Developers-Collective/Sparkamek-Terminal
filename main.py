from data.CompilerWorker import CompilerWorker
from data.LogType import LogType
import colorama, sys, os, json, pick



os.chdir(os.path.dirname(os.path.realpath(__file__)))
colorama.init(autoreset = True)

neutral_color = colorama.Fore.WHITE
bracket_color = colorama.Fore.LIGHTBLACK_EX
simple_logs: bool = False



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



def main():
    global simple_logs

    if not os.path.isfile('./config.json'):
        print(format_msg('No config.json found', LogType.Error))
        input('Press enter to exit...')
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

    assert (devkitppc_path is not None and os.path.isdir(devkitppc_path)), 'Unable to find devkitPPC path. Please set it manually in config.json'

    projects: list[dict] = config['projects']

    if len(projects) == 0:
        print(format_msg('No projects found in config.json', LogType.Error))
        input('Press enter to exit...')
        return

    option = ''
    index = 0
    options = [f'{project["name"]}' for project in projects] + ['[Exit]']
    show_menu = len(options) > 2

    while True:
        if (show_menu):
            option, index = pick.pick(
                options,
                '================<( Select a project to compile )>================\n       (Use arrow keys to navigate, press enter to select)',
                indicator = f'>',
                default_index = index
            )
            if option == '[Exit]': break

        project = projects[index]

        simple_logs = project['simpleLogs']

        if not os.path.exists(project['path']):
            print(format_msg(f'Unable to find path for project {project["name"]}', LogType.Error))
            os.system('bash -c \'read -s -n 1 -p "Press any key to continue..."\'')
            os.system('clear')
            break

        worker = CompilerWorker(
            data = project,
            devkitppc_path = devkitppc_path
        )
        worker.log_simple.connect(log_simple)
        worker.log_complete.connect(log_complete)
        worker.run()

        show_menu = True

        os.system('bash -c \'read -s -n 1 -p "Press any key to continue..."\'')
        os.system('clear')



if __name__ == "__main__":
    main()
