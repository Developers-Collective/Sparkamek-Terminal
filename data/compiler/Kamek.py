#----------------------------------------------------------------------

    # Libraries
from typing import Any
import binascii, os, os.path, shutil, struct, subprocess, sys, yaml, elftools.elf.elffile, dataclasses, difflib, colorama
from .Hooks import Hooks as hooks
from .MissingSymbol import MissingSymbol
from .CannotFindFunctionException import CannotFindFunctionException
from .MatchingFuncSymbol import MatchingFuncSymbol
from .FuncSymbol import FuncSymbol

from ..LogType import LogType
from ..ProjectException import ProjectException
from ..Signal import Signal
#----------------------------------------------------------------------

#   Setup
startupinfo = {}
if sys.platform == 'win32':
    startupinfo['startupinfo'] = subprocess.STARTUPINFO()
    startupinfo['startupinfo'].dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo['startupinfo'].wShowWindow = subprocess.SW_HIDE
#----------------------------------------------------------------------

    # Class
@dataclasses.dataclass
class KamekConfig:
    verbose: bool = True
    gcc_path: str = ''
    gcc_type: str = 'powerpc-eabi'
    use_rels: bool = True
    use_mw: bool = False
    mw_path: str = 'tools/cw/'
    filt_path: str = 'tools/c++filt/'
    use_wine: bool = False
    show_cmd: bool = False
    keep_temp: bool = False
    fast_hack: bool = False
    gcc_append_exe: bool = False

    @property
    def delete_temp(self) -> bool:
        return not self.keep_temp



class DyLinkCreator:
    R_PPC_ADDR32 = 1
    R_PPC_ADDR16_LO = 4
    R_PPC_ADDR16_HI = 5
    R_PPC_ADDR16_HA = 6
    R_PPC_REL24 = 10

    VALID_RELOCS = set([1, 4, 5, 6, 10])

    def __init__(self, controller: 'KamekController', other: 'DyLinkCreator' = None) -> None:
        self._controller = controller

        if other:
            self._relocs = other._relocs[:]

            self._targets = other._targets[:]
            self._target_lookups = other._target_lookups.copy()
        else:
            self._relocs = []

            self._targets = []
            self._target_lookups = {}

        self.elf = None

    def set_elf(self, stream) -> None:
        if self.elf != None:
            raise ValueError('ELF already set')

        self.elf = elftools.elf.elffile.ELFFile(stream)
        self.code = self.elf.get_section_by_name('.text').data()

        self._add_relocs(self.elf.get_section_by_name('.rela.text'))

    def _add_relocs(self, section: Any) -> None:
        sym_values = {}
        sym_section = self.elf.get_section_by_name('.symtab')

        for reloc in section.iter_relocations():
            entry = reloc.entry
            #print(entry)

            sym_id = entry['r_info_sym']
            try:
                sym_value, sym_name = sym_values[sym_id]
            except KeyError:
                sym = sym_section.get_symbol(sym_id)
                sym_value = sym.entry['st_value']
                sym_name = sym.name
                sym_values[sym_id] = (sym_value, sym_name)
            #print(hex(sym_value))

            self.add_reloc(entry['r_info_type'], entry['r_offset'], sym_value + entry['r_addend'], sym_name)

    def add_reloc(self, reltype, addr, target, name = "UNKNOWN NAME") -> None:
        if reltype not in self.VALID_RELOCS:
            raise ValueError('Unknown/unsupported rel type: %d (%x => %x)' % (reltype, addr, target))

        try:
            target_id = self._target_lookups[target]

        except KeyError:
            target_id = len(self._targets)
            self._target_lookups[target] = target_id
            self._targets.append(target)

        if target <= 0:
            if name != 'UNKNOWN NAME':
                self._controller.add_missing_symbol(MissingSymbol(addr, target, name))

        self._relocs.append((reltype, addr, target_id))

    def build_reloc_data(self) -> bytes:
        header_struct = struct.Struct('>8sI')

        rel_struct_pack = struct.Struct('>II').pack
        target_struct_pack = struct.Struct('>I').pack

        rel_data = map(lambda x: rel_struct_pack((x[0] << 24) | x[2], x[1]), self._relocs)
        target_data = map(target_struct_pack, self._targets)

        header = header_struct.pack(b'NewerREL', 12 + (len(self._relocs) * 8))

        return header + b''.join(rel_data) + b''.join(target_data)



class KamekModule:
    _required_fields = ['source_files']

    def __init__(self, controller: 'KamekController', filename: str) -> None:
        self._controller = controller
        # load the module data
        self.module_path = os.path.normpath(filename)
        self.module_name = os.path.basename(self.module_path)
        #self.module_dir = os.path.dirname(self.module_path)
        self.module_dir = 'processed'

        with open(f'{controller.cwd}/{self.module_path}', 'r', encoding = 'utf8') as f:
            self.raw_data = f.read()

        self.data = yaml.safe_load(self.raw_data)
        if not isinstance(self.data, dict):
            raise ValueError('the module file %s is an invalid format (it should be a YAML mapping)' % self.module_name)

        # verify it
        for field in self._required_fields:
            if field not in self.data:
                raise ValueError('Missing field in the module file %s: %s' % (self.module_name, field))



class KamekBuilder:
    def __init__(self, controller: 'KamekController', project, configs) -> None:
        self._controller = controller
        self.project = project
        self.configs = configs


    def build(self) -> None:
        self._controller.log_info_all('Starting build...')

        self._prepare_dirs()

        for config in self.configs:
            # if only_build != None and config['short_name'] not in only_build:
            #     continue

            self._set_config(config)

            #self._configTempDir = tempfile.mkdtemp()
            self._config_temp_dir = f'tmp'
            if os.path.isdir(f'{self._controller.cwd}/tmp'):
                shutil.rmtree(f'{self._controller.cwd}/tmp')
            os.mkdir(f'{self._controller.cwd}/tmp')
            self._controller.log_info('Temp files for this configuration are in: ' + self._config_temp_dir)

            if 'dynamic_link' in self._config and self._config['dynamic_link']:
                self.dynamic_link_base = DyLinkCreator(self._controller)
            else:
                self.dynamic_link_base = None

            self._builtCodeAddr = 0x80001800
            if 'code_address' in self.project.data:
                self._builtCodeAddr = self.project.data['code_address']

            # hook setup
            self._hook_contexts = {}
            for name, hookType in hooks.HookTypes.items():
                if hookType.has_context:
                    self._hook_contexts[hookType] = hookType.context_type()

            self._compile_modules()

            # figure out how many copies we need to build
            # this is a mess!
            try:
                if 'multi_build' in self._config:
                    self._multi_build = self._config['multi_build']
                else:
                    self._multi_build = {self._config['short_name']: self._config['linker_script']}

            except Exception:
                raise ProjectException(f'Invalid config file: "kamek_configs.yaml". Try using the same format as the NewerSMBW 1.3.0 one.', LogType.Error)

            keys = list(self._controller.version_ids.keys()) + ['pal']
            for s_name, s_script in self._multi_build.items():
                if s_name not in keys: continue

                self.current_build_name = s_name

                self._patches = []
                self._rel_patches = []
                self._hooks = []

                self._create_hooks()

                self._link(s_name, s_script)
                self._read_symbol_map()

                if self.dynamic_link_base:
                    self.dynamic_link = DyLinkCreator(self._controller, self.dynamic_link_base)
                    with open(self._current_out_file, 'rb') as infile:
                        self.dynamic_link.set_elf(infile)

                for hook in self._hooks:
                    hook.create_patches()

                self._create_patch(s_name)

            if self._controller.config.delete_temp:
                shutil.rmtree(f'{self._controller.cwd}/{self._config_temp_dir}')


    def _prepare_dirs(self) -> None:
        self._out_dir = self._controller.cwd + '/' + self.project.make_relative_path(self.project.data['output_dir'])
        self._controller.log_info('Project will be built in: ' + self._out_dir)

        if not os.path.isdir(self._out_dir):
            os.makedirs(self._out_dir)
            self._controller.log_info('Created that directory')


    def _set_config(self, config) -> None:
        self._config = config
        self._controller.log_info_all('&nbsp;', True)
        self._controller.log_info_all('Building for configuration: ' + config['friendly_name'])

        self.config_short_name = config['short_name']
        if 'rel_area_start' in config:
            self._rel_area = (config['rel_area_start'], config['rel_area_end'])
        else:
            self._rel_area = (-50, -50)


    def _create_hooks(self) -> None:
        self._controller.log_info('&nbsp;', True)
        self._controller.log_info('Creating hooks')

        for m in self.project.modules:
            if 'hooks' in m.data:
                for hook_data in m.data['hooks']:
                    assert 'name' in hook_data and 'type' in hook_data

                    #self._controller.log_info('Hook: %s : %s' % (m.moduleName, hookData['name']))

                    if hook_data['type'] in hooks.HookTypes:
                        hook_type = hooks.HookTypes[hook_data['type']]
                        hook = hook_type(self, m, hook_data)
                        self._hooks.append(hook)
                    else:
                        raise ValueError('Unknown hook type: %s' % hook_data['type'])


    def _filter_compilation_output(self, output: str) -> None:
        fasthack_content: list[str] = None

        if self._controller.config.fast_hack:
            with open(f'{self._controller.cwd}/{self._fast_cpp_path}', 'r') as infile:
                fasthack_content = infile.read().replace('\r', '').split('\n')


        lines = output.split('\n')
        warnings: dict[str, list] = {}
        errors: dict[str, list] = {}
        first_error: tuple = None

        digits = '0123456789'

        file = ''
        isfasthack = ''
        waves = ''
        fasthack_line: int = 0
        code = ''

        while lines:
            line = lines.pop(0).strip()

            if line.startswith('###'): continue


            if line.startswith('#    File: ') or line.startswith('#      In: '):
                file = line[11:]
                isfasthack = (file.replace('\\', '/').split('/')[-1].strip() == 'fasthack.cpp')
                continue


            if line.startswith('# Warning: '):
                waves = line[11:]
                details = []

                while lines[0].startswith('# '):
                    line = lines.pop(0)[1:].strip()
                    details.append(line)

                if self._controller.config.fast_hack and fasthack_content is not None and isfasthack:
                    index = fasthack_line
                    while ((not fasthack_content[index].startswith('// [Fasthack File Info] ')) or (not fasthack_content[index - 1].startswith('//')) or (not fasthack_content[index + 1].startswith('//'))) and index > 1:
                        index -= 1

                    fasthack_line_content = fasthack_content[index].replace('// [Fasthack File Info] ', '')
                    true_line = fasthack_line - index - 3

                    file = fasthack_line_content
                    fasthack_line = true_line

                if file not in warnings: warnings[file] = []
                warnings[file].append((fasthack_line, code, waves.find('^'), waves.rfind('^'), details))

                continue


            if line.startswith('#   Error: '):
                waves = line[11:]
                details = []

                while lines[0].startswith('# '):
                    line = lines.pop(0)[1:].strip()
                    details.append(line)

                if self._controller.config.fast_hack and fasthack_content is not None and isfasthack:
                    index = fasthack_line
                    while ((not fasthack_content[index].startswith('// [Fasthack File Info] ')) or (not fasthack_content[index - 1].startswith('//')) or (not fasthack_content[index + 1].startswith('//'))) and index > 1:
                        index -= 1

                    fasthack_line_content = fasthack_content[index].replace('// [Fasthack File Info] ', '')
                    true_line = fasthack_line - index - 3

                    file = fasthack_line_content
                    fasthack_line = true_line

                if file not in errors: errors[file] = []
                wavef = waves.find('^')
                wavel = waves.rfind('^')

                errors[file].append((fasthack_line, code, wavef, wavel, details))
                if first_error is None: first_error = (file, fasthack_line, code, wavef, wavel, details)

                continue

            if line.startswith('# -'): continue


            if line.startswith('# '):
                index = 1

                while line[index] == ' ' and index < len(line):
                    index += 1

                nb = ''

                while line[index] in digits and index < len(line):
                    nb += line[index]
                    index += 1

                if nb == '': continue

                fasthack_line = int(nb)
                code = line[index + 2:]

                continue

        if warnings or errors: self._controller.log_info_all('&nbsp;', True)

        for file in warnings:
            self._controller.log_warning(f'{colorama.Fore.LIGHTWHITE_EX}{file}{colorama.Style.RESET_ALL}:')

            for fasthack_line, code, pos1, pos2, details in warnings[file]:
                code_begin = code[:pos1]
                code_middle = code[pos1:pos2 + 1]
                code_end = code[pos2 + 1:]
                self._controller.log_warning(f'&nbsp;&nbsp;&nbsp;&nbsp;Line {fasthack_line}{colorama.Style.RESET_ALL}', True)
                self._controller.log_warning(f'&nbsp;&nbsp;&nbsp;&nbsp;{code_begin}{LogType.Warning.value}{code_middle}{colorama.Style.RESET_ALL}{code_end}', True)
                for detail in details:
                    self._controller.log_warning(f'&nbsp;&nbsp;&nbsp;&nbsp;{detail}{colorama.Style.RESET_ALL}', True)
                self._controller.log_warning('&nbsp;', True)


        if not first_error: return

        file, fasthack_line, code, pos1, pos2, details = first_error
        self._controller.log_simple.emit(f'{colorama.Fore.LIGHTWHITE_EX}{file}{colorama.Style.RESET_ALL}:', LogType.Error, False)

        code_begin = code[:pos1]
        code_middle = code[pos1:pos2 + 1]
        code_end = code[pos2 + 1:]
        self._controller.log_simple.emit(f'&nbsp;&nbsp;&nbsp;&nbsp;Line {fasthack_line}{colorama.Style.RESET_ALL}', LogType.Error, True)
        self._controller.log_simple.emit(f'&nbsp;&nbsp;&nbsp;&nbsp;{code_begin}{LogType.Error.value}{code_middle}{colorama.Style.RESET_ALL}{code_end}', LogType.Error, True)
        for detail in details:
            self._controller.log_simple.emit(f'&nbsp;&nbsp;&nbsp;&nbsp;{detail}{colorama.Style.RESET_ALL}', LogType.Error, True)
        self._controller.log_simple.emit('&nbsp;', LogType.Error, True)

        for file in errors:
            self._controller.log_complete.emit(f'{colorama.Fore.LIGHTWHITE_EX}{file}{colorama.Style.RESET_ALL}:', LogType.Error, False)

            for fasthack_line, code, pos1, pos2, details in errors[file]:
                code_begin = code[:pos1]
                code_middle = code[pos1:pos2 + 1]
                code_end = code[pos2 + 1:]
                self._controller.log_complete.emit(f'&nbsp;&nbsp;&nbsp;&nbsp;Line {fasthack_line}{colorama.Style.RESET_ALL}', LogType.Error, True)
                self._controller.log_complete.emit(f'&nbsp;&nbsp;&nbsp;&nbsp;{code_begin}{LogType.Error.value}{code_middle}{colorama.Style.RESET_ALL}{code_end}', LogType.Error, True)
                for detail in details:
                    self._controller.log_complete.emit(f'&nbsp;&nbsp;&nbsp;&nbsp;{detail}{colorama.Style.RESET_ALL}', LogType.Error, True)
                self._controller.log_complete.emit('&nbsp;', LogType.Error, True)


    def _compile_modules(self) -> None:
        self._controller.log_info('&nbsp;', True)
        self._controller.log_info('Compiling modules')

        if self._controller.config.use_mw:
            # metrowerks setup
            cc_command = ['%smwcceppc.exe' % self._controller.config.mw_path, '-I.', '-I-', '-I.', '-nostdinc', '-Cpp_exceptions', 'off', '-Os', '-proc', 'gekko', '-fp', 'hard', '-enum', 'int', '-sdata', '0', '-sdata2', '0', '-g', '-RTTI', 'off', '-use_lmw_stmw', 'on']
            as_command = ['%smwasmeppc.exe' % self._controller.config.mw_path, '-I.', '-I-', '-I.', '-nostdinc', '-proc', 'gekko', '-d', '__MWERKS__']

            try:
                if isinstance(self._config.get('defines'), dict): self._config['defines'] = list(self._config['defines'].keys())
                for d in self._config.get('defines', []) + self.project.data.get('defines', []):
                    cc_command.append('-d')
                    cc_command.append(d)
                    as_command.append('-d')
                    as_command.append(d)
                    self._controller.log_info(f'Defined: {d}')

                for i in self._config['include_dirs']:
                    cc_command.append('-I%s' % i)
                    #cc_command.append(i)
                    as_command.append('-I%s' % i)
                    #as_command.append(i)

                if self._controller.config.use_wine:
                    cc_command.insert(0, 'wine')
                    as_command.insert(0, 'wine')

            except Exception:
                raise ProjectException(f'Invalid config file: "kamek_configs.yaml". Try using the same format as the NewerSMBW 1.3.0 one.', LogType.Error)

        else:
            # gcc setup
            cc_command = ['%s%s-g++' % (self._controller.config.gcc_path, self._controller.config.gcc_type), '-nodefaultlibs', '-I.', '-fno-builtin', '-Os', '-fno-exceptions', '-fno-rtti', '-mno-sdata']
            as_command = cc_command

            try:
                for d in self._config.get('defines', []) + self.project.data.get('defines', []):
                    cc_command.append('-D%s' % d)

                for i in self._config['include_dirs']:
                    cc_command.append('-I%s' % i)

            except Exception:
                raise ProjectException(f'Invalid config file: "kamek_configs.yaml". Try using the same format as the NewerSMBW 1.3.0 one.', LogType.Error)


        self._module_files = []
        self._fast_cpp_path = None

        if self._controller.config.fast_hack:
            self._fast_cpp_path = os.path.join(self._config_temp_dir, 'fasthack.cpp')
            fast_cpp = open(f'{self._controller.cwd}/{self._fast_cpp_path}', 'w', encoding = 'utf8')

        for m in self.project.modules:
            for normal_sourcefile in m.data['source_files']:
                self._controller.log_info('Compiling %s : %s' % (m.module_name, normal_sourcefile))

                objfile = os.path.normpath(os.path.join(self._config_temp_dir, '%d.o' % self._controller.generate_unique_id())).replace('\\', '/')
                objfile = objfile.replace(self._controller.cwd, '')
                if objfile.startswith('/'): objfile = objfile[1:]

                sourcefile = os.path.normpath(os.path.join(self._controller.cwd, m.module_dir, normal_sourcefile)).replace('\\', '/')
                sourcefile = sourcefile.replace(self._controller.cwd, '')
                if sourcefile.startswith('/'): sourcefile = sourcefile[1:]

                if sourcefile.endswith('.o'):
                    new_command = ['cp', sourcefile, objfile]
                else:
                    # todo: better extension detection
                    if sourcefile.endswith('.s') or sourcefile.endswith('.S'):
                        command = as_command

                    elif sourcefile.endswith('.cpp') and self._controller.config.fast_hack:
                        fast_cpp.write('//\n// [Fasthack File Info] %s\n//\n\n' % sourcefile)
                        try:
                            with open(f'{self._controller.cwd}/{sourcefile}', 'r', encoding = 'utf8') as sf:
                                fast_cpp.write(sf.read())

                        except UnicodeError as e:
                            raise ProjectException(f'{sourcefile} >> Please use UTF-8 encoding for your source files as using multiple encodings can mess up CodeWarrior.', LogType.Error)

                        except Exception as e:
                            raise ProjectException(f'{sourcefile} >> {e}', LogType.Error)

                        fast_cpp.write('\n')
                        continue
                    else:
                        command = cc_command

                    new_command = command + ['-c', '-o', objfile, sourcefile]

                    if 'cc_args' in m.data:
                        new_command += m.data['cc_args']

                if self._controller.config.show_cmd:
                    self._controller.log_info(str(new_command))

                cwd = os.getcwd()

                try:
                    os.chdir(self._controller.cwd)
                    p = subprocess.Popen(new_command, stdout = subprocess.PIPE, *startupinfo)
                    output = p.communicate()[0].decode('utf-8')
                    error_val = p.poll()
                    os.chdir(cwd)

                    self._filter_compilation_output(output)

                except Exception as e:
                    os.chdir(cwd)
                    raise ProjectException(f'An error occured while calling the compiler.\nPlease make sure CodeWarrior is installed correctly into the tools folder.\nIf it\'s installed correctly, here is the error:\n{e}', LogType.Error)
                
                if error_val != 0:
                    if 'Driver Error' in output:
                        raise ProjectException(output, LogType.Error)

                    else:
                        raise ProjectException('Compiler returned %d - An error occurred while compiling %s' % (error_val, sourcefile), LogType.Error)

                self._module_files.append(objfile)

        if self._controller.config.fast_hack:
            fast_cpp.close()

            self._controller.log_info('Fast compilation!!')
            objfile = os.path.join(self._config_temp_dir, 'fasthack.o')

            new_command = cc_command + ['-c', '-o', objfile, self._fast_cpp_path]
            if self._controller.config.show_cmd:
                self._controller.log_info(str(new_command))

            cwd = os.getcwd()
            os.chdir(self._controller.cwd)
            p = subprocess.Popen(new_command, stdout = subprocess.PIPE, *startupinfo)
            output = p.communicate()[0].decode('utf-8')
            error_val = p.poll()
            os.chdir(cwd)

            self._filter_compilation_output(output)

            if error_val != 0:
                raise ProjectException('Compiler returned %d - An error occurred while compiling the fast hack' % error_val, LogType.Error)

            self._module_files.append(objfile)

        self._controller.log_success('Compilation complete')
        self._controller.log_success('&nbsp;', True)


    def _link(self, short_name, script_file) -> None:
        self._controller.log_info('Linking %s (%s)...' % (short_name, script_file))

        try:
            nice_name = '%s_%s' % (self._config['short_name'], short_name)

        except Exception:
                raise ProjectException(f'Invalid config file: "kamek_configs.yaml". Try using the same format as the NewerSMBW 1.3.0 one.', LogType.Error)

        self._current_map_file = '%s/%s_linkmap.map' % (self._out_dir, nice_name)
        outname = 'object.plf' if self.dynamic_link_base else 'object.bin'
        self._current_out_file = '%s/%s_%s' % (self._out_dir, nice_name, outname)

        exe = '.exe' if self._controller.config.gcc_append_exe else ''
        ld_command = ['%s%s-ld%s' % (self._controller.config.gcc_path, self._controller.config.gcc_type, exe), '-L.']
        ld_command.append('-o')
        ld_command.append(self._current_out_file)
        if self.dynamic_link_base:
            ld_command.append('-r')
            ld_command.append('--oformat=elf32-powerpc')
        else:
            ld_command.append('--oformat=binary')
            ld_command.append('-Ttext')
            ld_command.append('0x%08X' % self._builtCodeAddr)
        ld_command.append('-T')
        ld_command.append(script_file)
        ld_command.append('-Map')
        ld_command.append(self._current_map_file)
        ld_command.append('--no-demangle') # for debugging
        #ld_command.append('--verbose')
        ld_command += self._module_files

        if self._controller.config.show_cmd:
            self._controller.log_info(str(ld_command))

        cwd = os.getcwd()
        os.chdir(self._controller.cwd)
        error_val = subprocess.call(ld_command, *startupinfo)
        os.chdir(cwd)

        if error_val != 0:
            raise ProjectException('ld returned %d' % error_val, LogType.Error)

        self._controller.log_success_all('Successfully linked %s' % short_name)


    def _read_symbol_map(self) -> None:
        self._controller.log_info('Reading symbol map')

        self._symbols = []

        with open(self._current_map_file, 'r') as file:

            for line in file:
                if '__text_start' in line:
                    self._text_seg_start = int(line.split()[0],0)
                    break

            # now read the individual symbols
            # this is probably a bad method to parse it, but whatever
            for line in file:
                if '__text_end' in line:
                    self._text_seg_end = int(line.split()[0],0)
                    break

                if not line.startswith('                '): continue

                sym = line.split()
                sym[0] = int(sym[0],0)
                self._symbols.append(sym)

            # we've found __text_end, so now we should be at the output section
            current_end_address = self._text_seg_end

            for line in file:
                if line[0] == '.':
                    # probably a segment
                    data = line.split()
                    if len(data) < 3: continue

                    seg_addr = int(data[1],0)
                    seg_size = int(data[2],0)

                    if seg_addr+seg_size > current_end_address:
                        current_end_address = seg_addr + seg_size

            self._code_start = self._text_seg_start
            self._code_end = current_end_address

        self._controller.log_info('Read, %d symbol(s) parsed' % len(self._symbols))


        # next up, run it through c++filt
        self._controller.log_info('Running c++filt')
        opsys = sys.platform
        if opsys == 'darwin': opsys = 'osx'
        self._controller.log_info('%s/%s/%s-c++filt' % (self._controller.config.filt_path, opsys, self._controller.config.gcc_type))

        cwd = os.getcwd()
        try:
            os.chdir(self._controller.cwd)
            p = subprocess.Popen('%s/%s/%s-c++filt' % (self._controller.config.filt_path, opsys, self._controller.config.gcc_type), stdin = subprocess.PIPE, stdout = subprocess.PIPE, *startupinfo)
            os.chdir(cwd)

        except Exception as e:
            os.chdir(cwd)
            raise ProjectException(f'An error occured while calling c++filt.\nPlease make sure c++filt is installed correctly into the tools folder.\nIf it\'s installed correctly, here is the error:\n{e}', LogType.Error)

        symbol_name_list = [sym[1] for sym in self._symbols]
        filt_result = p.communicate('\n'.join(symbol_name_list).encode('utf-8'))
        filtered_symbols = filt_result[0].decode('utf-8').split('\n')

        for sym, filt in zip(self._symbols, filtered_symbols):
            sym.append(filt.strip())

        self._controller.log_success('Done. All symbols complete.')
        self._controller.log_success('Generated code is at 0x%08X .. 0x%08X' % (self._code_start, self._code_end - 4))


    def find_func_by_symbol(self, find_symbol: str) -> int:
        for sym in self._symbols:
            #if show_cmd:
            #   out = "0x%08x - %s - %s" % (sym[0], sym[1], sym[2])
            #   self._controller.log_info(out)
            if sym[2] == find_symbol:
                return sym[0]

        def similar(a: str, b: str) -> float:
            b_fn = b.split('(')
            if len(b_fn) > 1:
                b_fn = b_fn[0]
                a_fn = a.split('(')[0]
                if a_fn == b_fn:
                    return 1.0

                return (difflib.SequenceMatcher(None, a, b).ratio() + difflib.SequenceMatcher(None, a.split('(')[0], b.split('(')[0]).ratio()) / 2

            return difflib.SequenceMatcher(None, a, b).ratio()

        raise CannotFindFunctionException(
            str(find_symbol),
            sorted([MatchingFuncSymbol(sym[0], sym[2]) for sym in self._symbols if similar(sym[2], find_symbol) > 0.6], key = lambda x: similar(x.name, find_symbol), reverse=True)
        )


    def add_patch(self, offset, data) -> None:
        if offset >= self._rel_area[0] and offset <= self._rel_area[1] and self._controller.config.use_rels:
            self._rel_patches.append((offset, data))
        else:
            self._patches.append((offset, data))


    def _create_patch(self, short_name: str) -> None:
        self._controller.log_info('Creating patch')

        try:
            nice_name = '%s_%s' % (self._config['short_name'], short_name)

        except Exception:
                raise ProjectException(f'Invalid config file: "kamek_configs.yaml". Try using the same format as the NewerSMBW 1.3.0 one.', LogType.Error)

        # convert the .rel patches to KamekPatcher format
        if len(self._rel_patches) > 0:
            kamekpatch = self._controller.generate_kamek_patches(self._rel_patches)
            #self._patches.append((0x817F4800, kamekpatch))
            self._patches.append((0x80002F60, kamekpatch))

        if self.dynamic_link:
            # put together the dynamic link files
            with open(f'{self._out_dir}/{nice_name}_dlcode.bin', 'wb') as dlcode:
                dlcode.write(self.dynamic_link.code)

            with open(f'{self._out_dir}/{nice_name}_dlrelocs.bin', 'wb') as dlrelocs:
                dlrelocs.write(self.dynamic_link.build_reloc_data())

        else:
            # add the outfile as a patch if not using dynamic linking
            with open(f'{self._controller.cwd}/{self._current_out_file}', 'rb') as file:
                patch = (self._code_start, file.read())

            self._patches.append(patch)

        # generate a Riivolution patch
        with open(f'{self._out_dir}/{nice_name}_riiv.xml', 'w') as riiv:
            for patch in self._patches:
                riiv.write(self._controller.generate_riiv_mempatch(*patch) + '\n')

        # generate an Ocarina patch
        with open(f'{self._out_dir}/{nice_name}_ocarina.txt', 'w') as ocarina:
            for patch in self._patches:
                ocarina.write(self._controller.generate_ocarina_patch(*patch) + '\n')

        # generate a KamekPatcher patch
        with open(f'{self._out_dir}/{nice_name}_loader.bin', 'wb') as kpatch:
            kpatch.write(self._controller.generate_kamek_patches(self._patches))

        self._controller.log_success('Patches generated')



class KamekProject:
    _required_fields = ['output_dir', 'modules']

    def __init__(self, controller: 'KamekController', filename: str, configs: dict) -> None:
        self._controller = controller
        # load the project data
        self.project_path = os.path.abspath(filename)
        self.project_name = os.path.basename(self.project_path)
        self.project_dir = '' #os.path.dirname(self.project_path)
        self.configs = configs

        with open(self.project_path, 'r', encoding = 'utf8') as f:
            self.raw_data = f.read()

        self.data = yaml.safe_load(self.raw_data)
        if not isinstance(self.data, dict):
            raise ValueError('The project file is an invalid format (it should be a YAML mapping)')

        # verify it
        for field in self._required_fields:
            if field not in self.data:
                raise ValueError('Missing field in the project file: %s' % field)

        # load each module
        self.modules = []
        for module_name in self.data['modules']:
            module_path = self.make_relative_path(module_name)
            self.modules.append(KamekModule(self._controller, module_path))


    def make_relative_path(self, path) -> str:
        return os.path.normpath(os.path.join(self.project_dir, path))


    def build(self) -> tuple[FuncSymbol]:
        # compile everything in the project
        builder = KamekBuilder(self._controller, self, self.configs)
        builder.build()

        return (FuncSymbol(s[0], s[1], s[2]) for s in builder._symbols)



class KamekController:
    log_simple = Signal(str, LogType, bool)
    log_complete = Signal(str, LogType, bool)

    _u32 = struct.Struct('>I')

    def __init__(self, cwd: str, project_path: str, base_version: str, version_ids: dict) -> None:
        super(KamekController, self).__init__()

        self._project_path = project_path
        self._cwd = cwd
        self._base_version = base_version
        self._version_ids = version_ids
        self._config = None

        self._current_unique_id = 0
        self._missing_symbols: dict[str, MissingSymbol] = {}


    def add_missing_symbol(self, symbol: MissingSymbol) -> None:
        self.log_complete.emit(f'The following reloc ({symbol.addr:x}) points to {symbol.target:d}: Is this right? {LogType.Warning.value}{symbol.name}{colorama.Style.RESET_ALL}', LogType.Warning, False)
        if symbol.name not in self._missing_symbols: self._missing_symbols[symbol.name] = symbol


    def set_config(self, config: KamekConfig | str) -> None:
        self._config = config


    def _read_configs(self, config_path: str) -> dict:
        with open(config_path, 'r') as f:
            data = f.read()

        return yaml.safe_load(data)


    @property
    def cwd(self) -> str:
        return self._cwd

    @property
    def _project_full_path(self) -> str:
        return f'{self._cwd}/{self._project_path}'

    @property
    def config(self) -> KamekConfig:
        return self._config

    @property
    def version_ids(self) -> dict:
        return self._version_ids


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

    def log_success_all(self, msg: str, invisible: bool = False) -> None:
        msg = msg.strip()
        if not msg: return
        self.log_complete.emit(msg, LogType.Success, invisible)
        self.log_simple.emit(msg, LogType.Success, invisible)


    def run(self) -> tuple[tuple[MissingSymbol], tuple[FuncSymbol]]:
        project = KamekProject(self, self._project_full_path, self._read_configs(f'{self._cwd}/kamek_configs.yaml'))
        func_symbols = project.build()

        return tuple(self._missing_symbols.values()), func_symbols


    def generate_unique_id(self) -> int:
        # this is used for temporary filenames, to ensure that .o files
        # do not overwrite each other
        self._current_unique_id += 1
        return self._current_unique_id


    def align_addr_up(self, addr: int, align: int) -> int:
        align -= 1
        return (addr + align) & ~align


    def generate_riiv_mempatch(self, offset: int, data: bytes) -> str:
        return '<memory offset="0x%08X" value="%s" />' % (offset, binascii.hexlify(data))


    def generate_ocarina_patch(self, dest_offset: int, data: bytes) -> str:
        out = []
        count = len(data)

        sourceOffset = 0
        dest_offset -= 0x80000000
        for i in range(count >> 2):
            out.append('%08X %s' % (dest_offset | 0x4000000, binascii.hexlify(data[sourceOffset:sourceOffset+4])))
            sourceOffset += 4
            dest_offset += 4

        # take care
        remainder = count % 4
        if remainder == 3:
            out.append('%08X 0000%s' % (dest_offset | 0x2000000, binascii.hexlify(data[sourceOffset:sourceOffset+2])))
            out.append('%08X 000000%02x' % (dest_offset, data[sourceOffset+2]))
        elif remainder == 2:
            out.append('%08X 0000%s' % (dest_offset | 0x2000000, binascii.hexlify(data[sourceOffset:sourceOffset+2])))
        elif remainder == 1:
            out.append('%08X 000000%02x' % (dest_offset, data[sourceOffset]))

        return '\n'.join(out)


    def generate_kamek_patches(self, patchlist: list[tuple[int, bytes]]) -> bytes:
        kamekpatch = b''
        for patch in patchlist:
            if len(patch[1]) > 4:
                # block patch
                kamekpatch += self._u32.pack(self.align_addr_up(len(patch[1]), 4) // 4)
                kamekpatch += self._u32.pack(patch[0])
                kamekpatch += patch[1]
                # align it
                if len(patch[1]) % 4 != 0:
                    kamekpatch += b'\0' * (4 - (len(patch[1]) % 4))
            else:
                # single patch
                kamekpatch += self._u32.pack(patch[0])
                kamekpatch += patch[1]

        kamekpatch += self._u32.pack(0xFFFFFFFF)
        return kamekpatch
#----------------------------------------------------------------------
