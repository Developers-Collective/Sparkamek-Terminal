#----------------------------------------------------------------------

    # Libraries
import dataclasses, typing, re, yaml, os

from data.lib.cli.CLIConstants import CLIConstants
from ..LogType import LogType
from ..ProjectException import ProjectException
from ..Signal import Signal
#----------------------------------------------------------------------

    # Class
class AddressMapper:
    @dataclasses.dataclass
    class Mapping:
        start: int = None
        end: int = None
        delta: int = None

        def overlaps(self, other: 'AddressMapper.Mapping'):
            return (self.end >= other.start) and (self.start <= other.end)

        def __str__(self):
            return f'{self.start:08X}-{self.end:08X}: {"+" if self.delta >= 0 else "-"}0x{abs(self.delta)}'

        def __repr__(self):
            return f'<mapping {self!s}>'


    # base: 'AddressMapper' = None

    def __init__(self, base: 'AddressMapper' = None) -> None:
        super(AddressMapper, self).__init__()
        self._mappings: list[AddressMapper.Mapping] = []
        self._base: AddressMapper = base


    @property
    def base(self) -> 'AddressMapper':
        return self._base
    
    @base.setter
    def base(self, value: 'AddressMapper') -> None:
        self._base = value


    def add_mapping(self, start: int, end: int, delta: int) -> None:
        if start > end:
            raise ValueError(f'cannot map {start:08X}-{end:08X} as start is higher than end')

        new_mapping = self.Mapping(start, end, delta)

        for mapping in self._mappings:
            if mapping.overlaps(new_mapping):
                raise ValueError(f'mapping "{new_mapping}" overlaps with earlier mapping "{mapping}"')

        self._mappings.append(new_mapping)

    def remap(self, input: int) -> int:
        if self.base is not None:
            input = self.base.remap(input)

        for mapping in self._mappings:
            if mapping.start <= input <= mapping.end:
                # print(f'[REMAP] {mapping.start:X}-{mapping.end:X}: {mapping.delta:X} => {input:X} => {input + mapping.delta:X}')
                return input + mapping.delta

        return input

    def demap(self, input: int) -> int:
        for mapping in self._mappings:
            if (mapping.start + mapping.delta) <= input <= (mapping.end + mapping.delta):
                input = input - mapping.delta
                break

        if self.base is not None:
            input = self.base.demap(input)

        return input

    def demap_reverse(self, input: int) -> int:
        for mapping in self._mappings:
            if mapping.start <= input <= mapping.end:
                # print(f'[DEMAP] {mapping.start:X}-{mapping.end:X}: {mapping.delta:X} => {input:X} => {input + mapping.delta:X}')
                input = input + mapping.delta
                break

        if self.base is not None:
            input = self.base.demap_reverse(input)

        return input

    def items(self) -> list[Mapping]:
        return self._mappings.copy()

    def __str__(self) -> str:
        return '\n'.join([str(x) for x in self._mappings])



class AddressMapperController:
    log_simple = Signal(str, LogType, bool)
    log_complete = Signal(str, LogType, bool)

    def __init__(self, cwd: str, project_path: str, base_version: str, version_ids: dict) -> None:
        super(AddressMapperController, self).__init__()

        self._project_path = project_path
        self._cwd = cwd

        self._base_version = base_version
        self._version_ids = version_ids


    @property
    def _project_full_path(self) -> str:
        return f'{self._cwd}/{self._project_path}'


    def run(self) -> None:
        path = f'{self._cwd}/tools/versions-nsmbw.txt'
        if not os.path.exists(path):
            path = './data/game/nsmbw/versions/versions-nsmbw.txt'
        
        if not os.path.exists(path):
            raise ProjectException(f'Unable to find "{LogType.Error.value}versions-nsmbw.txt{CLIConstants.Reset}" at "{self._cwd}/tools"', LogType.Error)

        with open(path, 'r', encoding = 'utf-8') as infile:
            try: mappers = AddressMapperController.read_version_info(infile)
            except ValueError as e: raise ProjectException(str(e), LogType.Error)
            except ProjectException as e: raise e

        if not os.path.isdir(f'{self._cwd}/processed'):
            os.mkdir(f'{self._cwd}/processed')

        for x_id, txt_id in self._version_ids.items():
            try: self._do_mapfile(f'kamek_{self._base_version}.x', f'kamek_{x_id}.x', mappers[txt_id])
            except FileNotFoundError: raise ProjectException(f'Unable to find "{LogType.Error.value}kamek_{self._base_version}.x{CLIConstants.Reset}" at "{self._cwd}"', LogType.Error)
            except KeyError: raise ProjectException(f'Unable to find version {LogType.Error.value}{txt_id}{CLIConstants.Reset} in {self._cwd}/tools/versions-nsmbw.txt', LogType.Error)
            except Exception as e: raise ProjectException(str(e), LogType.Error)

        already_done = set()
        try: self._do_project(self._project_full_path, already_done, mappers)
        except FileNotFoundError as e: raise ProjectException(str(e), LogType.Error)


    @staticmethod
    def read_version_info(f: typing.TextIO) -> dict[str, AddressMapper]:
        mappers = {'default': AddressMapper()}

        comment_regex = re.compile(r'^\s*#')
        empty_line_regex = re.compile(r'^\s*$')
        section_regex = re.compile(r'^\s*\[([a-zA-Z0-9_.]+)\]$')
        extend_regex = re.compile(r'^\s*extend ([a-zA-Z0-9_.]+)\s*(#.*)?$')
        mapping_regex = re.compile(r'^\s*([a-fA-F0-9]{8})-((?:[a-fA-F0-9]{8})|\*)\s*:\s*([-+])0x([a-fA-F0-9]+)\s*(#.*)?$')
        current_version_name: str = None
        current_version: AddressMapper = None

        for line in f:
            line = line.rstrip('\n')

            if empty_line_regex.match(line):
                continue
            if comment_regex.match(line):
                continue

            match = section_regex.match(line)
            if match:
                # New version
                current_version_name = match.group(1)
                if current_version_name in mappers:
                    raise ValueError(f'Versions file contains duplicate version name {LogType.Error.value}{current_version_name}{CLIConstants.Reset}')

                current_version = AddressMapper()
                mappers[current_version_name] = current_version
                continue

            if current_version is not None:
                # Try to associate something with the current version
                match = extend_regex.match(line)
                if match:
                    base_name = match.group(1)
                    if base_name not in mappers:
                        raise ValueError(f'Version {current_version_name} extends unknown version {LogType.Error.value}{base_name}{CLIConstants.Reset}')
                    if current_version.base is not None:
                        raise ValueError(f'Version {current_version_name} already extends a version')

                    current_version._base = mappers[base_name]
                    continue

                match = mapping_regex.match(line)
                if match:
                    start_address = int(match.group(1), 16)
                    if match.group(2) == '*':
                        end_address = 0xFFFFFFFF
                    else:
                        end_address = int(match.group(2), 16)

                    delta = int(match.group(4), 16)
                    if match.group(3) == '-':
                        delta = -delta

                    current_version.add_mapping(start_address, end_address, delta)
                    continue

            raise ProjectException(f'Unrecognised line in versions file: {LogType.Error.value}{line}{CLIConstants.Reset}', LogType.Error)

        return mappers


    def _do_mapfile(self, src: str, dest: str, mapper: AddressMapper) -> None:
        new = []
        with open(f'{self._cwd}/{src}') as f:
            mapfile = [x.rstrip() for x in f]

        for line in mapfile:
            pos = line.find('= 0x80')
            if pos != -1:
                oldoffs = line[pos+2:pos+12]
                newoffs = mapper.remap(int(oldoffs, 16))
                line = line.replace(oldoffs, str(newoffs))

            new.append(line + '\n')

        with open(f'{self._cwd}/{dest}', 'w') as f:
            f.writelines(new)


    def _work_on_hook(self, hook: dict, name: str, mapper: AddressMapper) -> None:
        error = 'Missing hook type'
        try:
            t = hook['type']

            if t == 'patch':
                error = 'Missing address'
                hook[f'addr_{name}'] = mapper.remap(hook[f'addr_{self._base_version}'])

            elif t == 'branch_insn' or t == 'add_func_pointer':
                error = 'Missing source address'
                hook[f'src_addr_{name}'] = mapper.remap(hook[f'src_addr_{self._base_version}'])

                if f'target_func_{self._base_version}' in hook:
                    error = 'Missing target function'
                    hook[f'target_func_{name}'] = mapper.remap(hook[f'target_func_{self._base_version}'])

            elif t == 'nop_insn':
                error = 'Missing area'
                area = hook[f'area_{self._base_version}']

                if isinstance(area, list):
                    start = mapper.remap(area[0])
                    new_area = [start, start + (area[1] - area[0])]
                else:
                    new_area = mapper.remap(area)

                hook[f'area_{name}'] = new_area

        except KeyError:
            ret = (f'Key Error {LogType.Error.value}{error}{CLIConstants.Reset} in {name}', LogType.Error, False)
            self.log_simple.emit(*ret)
            self.log_complete.emit(*ret)


    def _do_module(self, src: str, dest: str, mappers: dict[str, AddressMapper]) -> None:
        try:
            with open(f'{self._cwd}/{src}') as f:
                m = yaml.safe_load(f.read())

        except FileNotFoundError as e:
            raise ProjectException(f'Unable to find "{LogType.Error.value}{e.filename}{CLIConstants.Reset}" at "{self._cwd}"', LogType.Error)
        
        except yaml.MarkedYAMLError as e:
            error = e.problem_mark.get_snippet().split('\n')[0]
            symbols_str = e.problem_mark.get_snippet().split('\n')[1]
            index_start, index_end = symbols_str.find('^'), symbols_str.rfind('^')
            error_highlight = f'{error[:index_start]}{LogType.Error.value}{error[index_start:index_end+1]}{CLIConstants.Reset}{error[index_end+1:]}'

            error_msg = f'{e.problem} {e.context}'

            raise ProjectException(f'Error parsing module file at line {e.problem_mark.line + 1}, column {e.problem_mark.column + 1}: {LogType.Error.value}{src}{CLIConstants.Reset}\n{error_msg}\n{error_highlight}', LogType.Error)

        for x_id, txt_id in self._version_ids.items():
            mapper = mappers[txt_id]
            if 'hooks' in m:
                for hook in m['hooks']:
                    self._work_on_hook(hook, x_id, mapper)

        with open(f'{self._cwd}/{dest}', 'w') as f:
            f.write(yaml.dump(m))


    def _do_project(self, f: str, already_done: set, mappers: dict[str, AddressMapper]) -> None:
        try:
            with open(f) as infile:
                proj = yaml.safe_load(infile.read())

        except FileNotFoundError as e:
            raise ProjectException(f'Unable to find "{LogType.Error.value}{e.filename}{CLIConstants.Reset}" at "{self._cwd}"', LogType.Error)
        
        except yaml.MarkedYAMLError as e:
            error = e.problem_mark.get_snippet().split('\n')[0]
            symbols_str = e.problem_mark.get_snippet().split('\n')[1]
            index_start, index_end = symbols_str.find('^'), symbols_str.rfind('^')
            error_highlight = f'{error[:index_start]}{LogType.Error.value}{error[index_start:index_end+1]}{CLIConstants.Reset}{error[index_end+1:]}'

            error_msg = f'{e.problem} {e.context}'

            raise ProjectException(f'Error parsing module file at line {e.problem_mark.line + 1}, column {e.problem_mark.column + 1}: {LogType.Error.value}{f}{CLIConstants.Reset}\n{error_msg}\n{error_highlight}', LogType.Error)

        if 'modules' in proj:
            for m in proj['modules']:
                if m not in already_done:
                    already_done.add(m)
                    self._do_module(m.replace('processed/', ''), m, mappers)
#----------------------------------------------------------------------
