#----------------------------------------------------------------------

    # Libraries
import os, yaml, sys, difflib, timeit
from pathlib import Path

from data.lib.LogType import LogType
from data.lib.ProjectException import ProjectException
from data.lib.cli.CLIConstants import CLIConstants
from .compiler import *
from .Signal import Signal
#----------------------------------------------------------------------

    # Class
class CompilerWorker:
    done = Signal()
    error = Signal(str)
    log_simple = Signal(str, LogType, bool)
    log_complete = Signal(str, LogType, bool)
    new_symbols = Signal(tuple)

    def __init__(self, data: dict, devkitppc_path: str) -> None:
        self._data = data
        self._devkitppc_path = f'{devkitppc_path}/'

        path = os.path.abspath(data['path']).replace('\\', '/')

        self._project_path = os.path.basename(path)
        self._cwd = os.path.dirname(path)
        self._project_name = self._project_path.rstrip('.yaml')

        self._base_version = 'pal'
        self._version_ids = (
            ({'pal2': 'P2'} if (data.get('generatePALv2', None) or data.get('generatePAL', None)) else {}) |
            ({'ntsc': 'E1'} if (data.get('generateNTSCv1', None) or data.get('generateNTSC', None)) else {}) |
            ({'ntsc2': 'E2'} if (data.get('generateNTSCv2', None) or data.get('generateNTSC', None)) else {}) |
            ({'jpn': 'J1'} if (data.get('generateJPv1', None) or data.get('generateJP', None)) else {}) |
            ({'jpn2': 'J2'} if (data.get('generateJPv2', None) or data.get('generateJP', None)) else {}) |
            ({'kor': 'K'} if data.get('generateKR', None) else {}) |
            ({'twn': 'W'} if data.get('generateTW', None) else {}) |
            ({'chn': 'C'} if data.get('generateCN', None) else {})
        )

        self._address_mapper_controller = AddressMapperController(self._cwd, self._project_path, self._base_version, self._version_ids)
        self._address_mapper_controller.log_simple.connect(self.log_simple.emit)
        self._address_mapper_controller.log_complete.connect(self.log_complete.emit)

        self._kamek_controller = KamekController(self._cwd, self._project_path, self._base_version, self._version_ids)
        self._kamek_controller.log_simple.connect(self.log_simple.emit)
        self._kamek_controller.log_complete.connect(self.log_complete.emit)


    @property
    def _project_full_path(self) -> str:
        return f'{self._cwd}/{self._project_path}'


    def run(self) -> None:
        self.log_info_all('Starting compilation...', False)

        start_time = timeit.default_timer()

        if not os.path.isfile(self._project_full_path):
            self.log_error(f'Cannot find project file at "{self._project_full_path}"', False)
            return self.error.emit(f'Cannot find project file at "{self._project_full_path}"')

        with open(self._project_full_path, 'r', encoding = 'utf-8') as f:
            project_data = yaml.safe_load(f)

        if not isinstance(project_data, dict):
            msg = 'The project file is an invalid format (it should be a YAML mapping)'
            self.log_error(msg, False)
            return self.error.emit(msg)

        if 'output_dir' not in project_data:
            msg = 'Missing output_dir field in the project file'
            self.log_error(msg, False)
            return self.error.emit(msg)

        self._asm_folder = Path(project_data['output_dir'])


        if not os.path.isdir(self._devkitppc_path):
            self.log_error(f'Cannot find devkitPPC at "{self._devkitppc_path}"', False)
            self.log_error(f'You can change this path in the global settings.', True)
            return self.error.emit(f'Cannot find devkitPPC at "{self._devkitppc_path}"')

        if sys.platform == 'win32':
            # Running on Windows
            kamekopts = {'gcc_append_exe': True}

        else:
            proc_version = Path('/proc/version')
            if proc_version.is_file() and 'microsoft' in proc_version.read_text().lower():  # https://stackoverflow.com/a/38859331/4718769
                # Running on WSL
                kamekopts = {'gcc_append_exe': True}

            else:
                # Running on Mac/Linux
                kamekopts = {'use_wine': True}

        self.log_info(f'Mapping addresses for {self._project_name}...', False)

        try: self._address_mapper_controller.run()

        except ProjectException as e:
            l = e.msg.split('\n')
            if not l:
                self.log_error('Internal error', False)
                return self.error.emit('Internal error')

            self.log_error(l[0], False)
            for line in l[1:]:
                self.log_error(line, True)

            return self.error.emit(e.msg)


        cw_path = ''

        for path in Path(self._cwd).glob('**/mwcceppc*'):
            if not path.is_file(): continue
            cw_path = str(path.parent.relative_to(self._cwd)) + '/'
            break

        if not cw_path:
            if os.path.isdir(f'{self._cwd}/tools/cw'):
                cw_path = 'tools/cw/'

            else:
                self.log_error(f'Cannot find CodeWarrior at "{self._cwd}/tools/cw".\nPlease make sure CodeWarrior is installed correctly into the tools folder.', False)
                self.log_error(f'You can find the installer here: {CLIConstants.MagentaColor.terminal_color}\"http://cache.nxp.com/lgfiles/devsuites/PowerPC/CW55xx_v2_10_SE.exe?WT_TYPE=IDE%20-%20Debug,%20Compile%20and%20Build%20Tools&WT_VENDOR=FREESCALE&WT_FILE_FORMAT=exe&WT_ASSET=Downloads&fileExt=.exe\"{CLIConstants.Reset}NXP \'CodeWarrior Special Edition\' for MPC55xx/MPC56xx v2.10.', True)
                self.log_error(f'If this direct link doesn\'t work, the original page is {CLIConstants.MagentaColor.terminal_color}\"http://web.archive.org/web/20160602205749/http://www.nxp.com/products/software-and-tools/software-development-tools/codewarrior-development-tools/downloads/special-edition-software:CW_SPECIALEDITIONS\"{CLIConstants.Reset}available on the Internet Archive.', True)
                return self.error.emit(f'Cannot find CodeWarrior at "{self._cwd}/tools/cw".')


        self._kamek_controller.set_config( # todo: get from settings (maybe?)
            KamekConfig(
                show_cmd = True,
                use_rels = False,
                use_mw = True,
                gcc_path = self._devkitppc_path,
                gcc_type = 'powerpc-eabi',
                mw_path = cw_path,
                filt_path = 'tools/c++filt/',
                fast_hack = True,
                nintendo_driver_mode = self._data.get('nintendoDriverMode', False),
                **kamekopts
            )
        )

        missing_symbols: tuple[MissingSymbol] = tuple()
        func_symbols: tuple[FuncSymbol] = tuple()
        try: missing_symbols, func_symbols = self._kamek_controller.run()

        except CannotFindFunctionException as e:
            self.log_error(f'Cannot find function: "{LogType.Error.value}{e.not_found_func}{CLIConstants.Reset}"', False)

            def make_diff(a: str, b: str) -> str:
                new_s = ''
                s = difflib.SequenceMatcher(None, a, b, autojunk = False)

                for tag, i1, i2, j1, j2 in s.get_opcodes():
                    if tag == 'equal': new_s += a[i1:i2]
                    elif tag == 'replace': new_s += make_span(b[j1:j2], LogType.Info)
                    # elif tag == 'delete': new_s += make_span(a[i1:i2], LogType.Error) # To prevent confusion, don't highlight deleted characters
                    elif tag == 'insert': new_s += make_span(b[j1:j2], LogType.Success)

                return new_s

            def make_span(s: str, log_type: LogType) -> str:
                return f'{log_type.value}{s}{CLIConstants.Reset}'

            if len(e.func_symbols) == 1:
                self.log_error(f'&nbsp;&nbsp;Did you mean "{make_diff(e.not_found_func, e.func_symbols[0].name)}"?', True)
                # self.log_error(f'&nbsp;&nbsp;&nbsp;&nbsp;→ {e.func_symbols[0].raw}', True)

            elif len(e.func_symbols) > 1:
                self.log_error(f'&nbsp;&nbsp;Did you mean one of these?', True)

                for func in e.func_symbols:
                    self.log_error(f'&nbsp;&nbsp;&nbsp;&nbsp;• {make_diff(e.not_found_func, func.name)}', True)
                    # self.log_error(f'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;→ {func.raw}', True)

                    # if func != e.func_symbols[-1]: self.log_error('&nbsp;', True)

            return self.error.emit(e.msg)

        except ProjectException as e:
            if 'Driver Error' in e.msg:
                func = lambda s, inv: self.log_complete.emit(s, LogType.Error, inv)
                self.log_error('An Driver Error occured while calling the compiler.', False)
                self.log_error('Please make sure the right version of CodeWarrior is installed into the tools folder.', True)
                self.log_error(f'You can find the installer here: {CLIConstants.MagentaColor.terminal_color}\"http://cache.nxp.com/lgfiles/devsuites/PowerPC/CW55xx_v2_10_SE.exe?WT_TYPE=IDE%20-%20Debug,%20Compile%20and%20Build%20Tools&WT_VENDOR=FREESCALE&WT_FILE_FORMAT=exe&WT_ASSET=Downloads&fileExt=.exe\"{CLIConstants.Reset}NXP \'CodeWarrior Special Edition\' for MPC55xx/MPC56xx v2.10.', True)
                self.log_error(f'If this direct link doesn\'t work, the original page is {CLIConstants.MagentaColor.terminal_color}\"http://web.archive.org/web/20160602205749/http://www.nxp.com/products/software-and-tools/software-development-tools/codewarrior-development-tools/downloads/special-edition-software:CW_SPECIALEDITIONS\"{CLIConstants.Reset}available on the Internet Archive.', True)

            else:
                func = self.log_error

            lines = e.msg.split('\n')
            first_line = lines.pop(0)
            func(first_line, False)

            for line in lines:
                func(line, True)

            return self.error.emit(e.msg)

        except Exception as e:
            self.log_error(str(e), False)
            return self.error.emit(str(e))

        self._build_folder = Path(f'{self._cwd}/{self._data.get("buildFolder", "Build")}')
        if not self._build_folder.is_dir():
            self._build_folder.mkdir()


        self.log_info('&nbsp;', True)

        def rename(name: str, key: str, key_all: str, version_name1: str, version_name2: str) -> None:
            if self._data.get(key, None) or (self._data.get(key_all, None) if key_all else False):
                try:
                    self.log_info(f'Renaming {name} files...', False)
                    self._copy_files(version_name1, version_name2)

                except FileNotFoundError as e:
                    self.log_warning(f'Cannot find {name} file ({os.path.basename(e.filename)}). Did you forget to add them to the compilation config?', False)

        rename('PALv1', 'generatePALv1', 'generatePAL', 'pal', 'EU_1')
        rename('PALv2', 'generatePALv2', 'generatePAL', 'pal2', 'EU_2')
        rename('NTSCv1', 'generateNTSCv1', 'generateNTSC', 'ntsc', 'US_1')
        rename('NTSCv2', 'generateNTSCv2', 'generateNTSC', 'ntsc2', 'US_2')
        rename('JPv1', 'generateJPv1', 'generateJP', 'jpn', 'JP_1')
        rename('JPv2', 'generateJPv2', 'generateJP', 'jpn2', 'JP_2')
        rename('KR', 'generateKR', None, 'kor', 'KR_3')
        rename('TW', 'generateTW', None, 'twn', 'TW_4')
        rename('CN', 'generateCN', None, 'chn', 'CN_5')

        if missing_symbols:
            self.log_simple.emit('&nbsp;', LogType.Info, True)
            self.log_simple.emit('Your code is missing the following symbols:', LogType.Warning, False)

            for symbol in missing_symbols:
                self.log_simple.emit(f'&nbsp;&nbsp;&nbsp;&nbsp;• {LogType.Warning.value}{symbol.name}{CLIConstants.Reset}', LogType.Warning, True)


        if path := self._data.get('outputFolder', None):
            self.log_info(f'Copying files to {path}...', False)

            if not os.path.isdir(path):
                os.makedirs(path)

            for file in self._build_folder.iterdir():
                if file.is_file():
                    file.replace(Path(self._cwd) / path / file.name)


        s = f'Compilation finished in {timeit.default_timer() - start_time:.2f} seconds.'

        self.log_info_all('&nbsp;', True)
        if missing_symbols: self.log_success(f'All done, but the game will crash at some point due to missing symbols.\n{s}', False)
        else: self.log_success(f'All done! {s}', False)

        self.new_symbols.emit(func_symbols)

        self.done.emit()

    def _copy_files(self, version_name_1: str, version_name_2: str) -> None:
        (Path(self._cwd) / self._asm_folder / f'n_{version_name_1}_loader.bin').replace(self._build_folder / f'System{version_name_2}.bin')
        (Path(self._cwd) / self._asm_folder / f'n_{version_name_1}_dlcode.bin').replace(self._build_folder / f'DLCode{version_name_2}.bin')
        (Path(self._cwd) / self._asm_folder / f'n_{version_name_1}_dlrelocs.bin').replace(self._build_folder / f'DLRelocs{version_name_2}.bin')

    def log_info(self, msg: str, invisible: bool = False) -> None:
        msg = msg.strip()
        if not msg: return
        self.log_complete.emit(msg, LogType.Info, invisible)

    def log_info_all(self, msg: str, invisible: bool = False) -> None:
        msg = msg.strip()
        if not msg: return
        self.log_complete.emit(msg, LogType.Info, invisible)
        self.log_simple.emit(msg, LogType.Info, invisible)

    def log_warning(self, msg: str, invisible: bool = False) -> None:
        msg = msg.strip()
        if not msg: return
        self.log_complete.emit(msg, LogType.Warning, invisible)
        self.log_simple.emit(msg, LogType.Warning, invisible)

    def log_error(self, msg: str, invisible: bool = False) -> None:
        msg = msg.strip()
        if not msg: return
        self.log_complete.emit(msg, LogType.Error, invisible)
        self.log_simple.emit(msg, LogType.Error, invisible)

    def log_success(self, msg: str, invisible: bool = False) -> None:
        msg = msg.strip()
        if not msg: return
        self.log_complete.emit(msg, LogType.Success, invisible)
        self.log_simple.emit(msg, LogType.Success, invisible)
#----------------------------------------------------------------------
