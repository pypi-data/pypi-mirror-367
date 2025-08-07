from falcon_logger import FalconLogger

from .arduino_shared import ArduinoShared
from .compile_cmd_json import CompileCmdJson
from .constants_version import ConstantsVersion
from .gbl import Gbl
from .osal import Osal
from .package_cpip import PackageCpip
from .package_opengl import PackageOpengl
from .svc import svc


# --------------------
## class to generate a makefile using a set of rules defined in python
class AlaMake:

    # --------------------
    ## constructor
    def __init__(self):
        svc.log = FalconLogger()
        svc.log.set_format('prefix')
        svc.gbl = Gbl()
        svc.osal = Osal  # not an instance, it is the class

        svc.log.line(f'OS name: {svc.gbl.os_name}')

        ## list of targets
        self._targets = []

        ## the file pointer to the makefile
        self._fp = None
        ## the current target
        self._tgt = None
        ## the list of rules
        self._rules = {}
        ## the list of help info
        self._help = {}
        svc.log.highlight('creating targets...')

    # --------------------
    ## abort session
    def abort(self, msg):
        print('here22')
        svc.abort(msg)

    # --------------------
    ## return True if OS is RPI
    @property
    def is_rpi(self):
        return svc.gbl.os_name == 'rpi'

    # --------------------
    ## return True if OS is Windows/Msys2
    @property
    def is_win(self):
        return svc.gbl.os_name == 'win'

    # --------------------
    ## return True if OS is macoOS
    @property
    def is_macos(self):
        return svc.gbl.os_name == 'macos'

    # --------------------
    ## return True if OS is Ubuntu
    @property
    def is_ubuntu(self):
        return svc.gbl.os_name == 'ubuntu'

    # --------------------
    ## return the version string for pyalamake
    @property
    def version(self):
        return ConstantsVersion.version

    # --------------------
    ## return ref to svc global
    # @return svc.gbl
    @property
    def gbl(self):
        return svc.gbl

    # --------------------
    ## return ref to svc log
    # @return svc.log
    @property
    def log(self):
        return svc.log

    # --------------------
    ## return ref to svc OSAL
    # @return svc.osal
    @property
    def osal(self):
        return svc.osal

    # --------------------
    ## for UT only
    # @return ref to svc
    @property
    def ut_svc(self):
        return svc

    # === cfg related

    # --------------------
    ## generate quiet rm for clean command
    #
    # @param val (bool) set cfg value to True to run quiet, or False to be verbose
    # @return None
    def cfg_quiet_clean(self, val=True):
        svc.gbl.quiet_clean = val

    # --------------------
    ## generate compile_commands.json file
    #
    # @param val (bool) set cfg value to True to gen, or False to skip
    # @return None
    def cfg_gen_compile_commands(self, val=True):
        svc.gbl.gen_compile_commands = val

    # --------------------
    ## crate an arduino shared target
    #
    # @return reference to arduino shared object
    def create_arduino_shared(self):
        return ArduinoShared()

    # --------------------
    ## create a target with the given name and type.
    # The current recognized target types:
    #  * cpp - a C++ app or library
    #  * c   - a C app or library
    #  * gtest - a unit test app for test C++
    #  * arduino - an arduino app
    #  * arduino-core - an arduino core
    #  * swig - a swig translation to python/ruby
    #  * manual - generate manual compilation steps
    #
    # @param target_name   the name of the new target
    # @param target_type   the type of the target
    # @param shared        whether this is a shared target (e.g. Arduino Core)
    def create(self, target_name, target_type, shared=None):
        type_mapper = {
            # do not put arduino_core here
            'cpp': self._create_cpp,
            'cpp-lib': self._create_cpp_lib,
            'c': self._create_c,
            'c-lib': self._create_c_lib,
            'gtest': self._create_gtest,
            'arduino': self._create_arduino,
            'swig': self._create_swig,
            'manual': self._create_manual,
        }

        for tgt in self._targets:
            if target_name == tgt.target:
                svc.abort(f'target name is already in use: {target_name}')
                return None  # pragma: no cover

        if target_type == 'arduino-core':
            create_fn = self._create_arduino_core
        else:
            create_fn = type_mapper.get(target_type, None)

        if create_fn is None:
            svc.log.err(f'unknown target type: {target_type}')
            svc.abort(f'valid target types: {" ".join(type_mapper.keys())} ')
            return None  # pragma: no cover

        return create_fn(target_name, shared)

    # --------------------
    ## create a target with cpp type
    #
    # @param target_name   the name of the new target
    # @param shared        (unused) whether this is a shared target
    def _create_cpp(self, target_name, shared=None):  # pylint: disable=unused-argument
        from .target_cpp import TargetCpp
        svc.log.line(f'create: {target_name}')
        return TargetCpp.create(self._targets, target_name)

    # --------------------
    ## create a target with cpp lib type
    #
    # @param target_name   the name of the new target
    # @param shared        (unused) whether this is a shared target
    def _create_cpp_lib(self, target_name, shared=None):  # pylint: disable=unused-argument
        from .target_cpp_lib import TargetCppLib
        svc.log.line(f'create: {target_name}')
        return TargetCppLib.create(self._targets, target_name)

    # --------------------
    ## create a target with c type
    #
    # @param target_name   the name of the new target
    # @param shared        (unused) whether this is a shared target
    def _create_c(self, target_name, shared=None):  # pylint: disable=unused-argument
        from .target_c import TargetC
        svc.log.line(f'create: {target_name}')
        return TargetC.create(self._targets, target_name)

    # --------------------
    ## create a target with c lib type
    #
    # @param target_name   the name of the new target
    # @param shared        (unused) whether this is a shared target
    def _create_c_lib(self, target_name, shared=None):  # pylint: disable=unused-argument
        from .target_c_lib import TargetCLib
        svc.log.line(f'create: {target_name}')
        return TargetCLib.create(self._targets, target_name)

    # --------------------
    ## create a target with gtest type
    #
    # @param target_name   the name of the new target
    # @param shared        (unused) whether this is a shared target
    def _create_gtest(self, target_name, shared=None):  # pylint: disable=unused-argument
        from .target_gtest import TargetGtest
        svc.log.line(f'create: {target_name}')
        return TargetGtest.create(self._targets, target_name)

    # --------------------
    ## create a target with arduino type
    #
    # @param target_name   the name of the new target
    # @param shared        whether this is a shared target (e.g. Arduino Core)
    def _create_arduino(self, target_name, shared=None):
        svc.log.line(f'create: {target_name}')
        from .target_arduino import TargetArduino
        return TargetArduino.create(self._targets, target_name, shared=shared)

    # --------------------
    ## create a target with arduino core type
    #
    # @param target_name   the name of the new target
    # @param shared        whether this is a shared target (e.g. Arduino Core)
    def _create_arduino_core(self, target_name, shared=None):
        svc.log.line(f'create: {target_name}')
        from .target_arduino_core import TargetArduinoCore
        return TargetArduinoCore.create(self._targets, target_name, shared=shared)

    # --------------------
    ## create a target with swig type
    #
    # @param target_name   the name of the new target
    # @param shared        (unused) whether this is a shared target
    def _create_swig(self, target_name, shared=None):  # pylint: disable=unused-argument
        from .target_swig import TargetSwig
        svc.log.line(f'create: {target_name}')
        return TargetSwig.create(self._targets, target_name)

    # --------------------
    ## create a target with manual type
    #
    # @param target_name   the name of the new target
    # @param shared        (unused) whether this is a shared target
    def _create_manual(self, target_name, shared=None):  # pylint: disable=unused-argument
        from .target_manual import TargetManual
        svc.log.line(f'create: {target_name}')
        return TargetManual.create(self._targets, target_name)

    # --------------------
    ## find a package to add to this target.
    # Current packages recognized:
    #  cpip.* - see CPIP for available packages
    #  opengl - OpenGL package for graphics
    #
    # @param pkgname  the package name to search for
    # @return package info
    def find_package(self, pkgname):
        if pkgname.startswith('cpip.'):
            pkg = PackageCpip()
        elif pkgname == 'opengl':
            pkg = PackageOpengl()
        else:
            svc.log.err(f'unknown package: {pkgname}')
            svc.abort()
            return 'unknown'  # not needed, but stops IDE and pylint warnings

        return pkg.find(pkgname)

    # -------------------
    ## get the cross-platform port (e.g. COM3) based on the vid-pid of the USB port.
    #
    # @param vid_pid   the USB VID/PID value
    # @return the port with the VID/PID value in it, or None if not found
    def get_port(self, vid_pid):
        try:
            import serial
        except ModuleNotFoundError:
            svc.log.warn(f'{"get_port": <15}: module pyserial is not installed')
            return None

        found_ports = []
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(ports):
            if vid_pid in hwid:
                svc.log.ok(f'{"get_port": <15}: found port {port}: {desc} [{hwid}]')
                return port
            # svc.log.dbg(f'port {port}: {desc} [{hwid}]')
            found_ports.append(f'port {port}: {desc} [{hwid}]')
        svc.log.err(f'{"get_port": <15}: vid-pid not found: "{vid_pid}"')
        svc.log.err(f'{"get_port": <15}: check USB is connected and powered on')
        svc.log.line('found these ports: >>')
        svc.log.num_output(found_ports)
        svc.log.line('<<')
        return None

    # === makefile related

    # --------------------
    ## generate makefile
    #
    # @param ut_path  (UT only) the path to the makefile to generate; default: Makefile
    # @return None
    def makefile(self, ut_path=None):
        svc.log.highlight('generating targets...')
        self._gather_targets()

        self._gen_root_makefile()
        if ut_path:
            path = ut_path
        else:
            path = f'Makefile.{svc.gbl.os_name}'
        with open(path, 'w', encoding='utf-8', newline='\n') as self._fp:
            svc.log.highlight(f'generating makefile {path}...')
            self._gen_rules()
            self._gen_targets()
            self._gen_clean()
            self._gen_help()
        svc.log.line('done')

    # --------------------
    ## gather all targets
    #
    # @return None
    def _gather_targets(self):
        self._rules = {}
        for tgt in self._targets:
            # uncomment to debug
            # svc.log.dbg(f'   source   : {tgt.sources}')

            tgt.check()
            tgt.gen_target()
            tgt.gen_clean()
            self._rules[tgt.target] = tgt.rules

    # --------------------
    ## generate all rules
    #
    # @return None
    def _gen_rules(self):
        # gen rule for all
        rule = 'all'
        rules_str = ''
        for tgt, rules in self._rules.items():
            rules_str += f' {tgt} '
            rules_str += ' '.join(rules)
        self._writeln(f'.PHONY : all clean help {rules_str}')

        # has to be first target found otherwise clion can't parse it
        self._gen_rule(rule, rules_str, f'build {rule}')

        # generate a single rule to build each target in total
        for rule, rules_deps in self._rules.items():
            rules_str = ' '.join(rules_deps)
            self._gen_rule(rule, rules_str, f'build {rule}')

        self._writeln('')

    # --------------------
    ## generate all targets
    #
    # @return None
    def _gen_targets(self):
        ccj = CompileCmdJson()
        for tgt in self._targets:
            ccj.init()
            self._writeln(f'# ==== {tgt.target}')
            for line in tgt.lines:
                ccj.get_info(line)
                self._writeln(line)

        ccj.save()

    # --------------------
    ## generate help info
    #
    # @return None
    def _gen_help(self):
        bslash = '\\'
        self._add_help('help', 'this help info')

        # gather all the help
        all_help = {}
        all_help.update(self._help)
        for tgt in self._targets:
            all_help.update(tgt.help)

        self._writeln('help:')
        self._writeln(f'\t@printf "Available targets:{bslash}n"')
        last_rule = 'help'
        for rule, desc in sorted(all_help.items()):
            if rule.startswith(f'{last_rule}-'):
                rule_pfx = '  '
            else:
                last_rule = rule
                rule_pfx = ''
            desc2 = desc.replace('"', f'{bslash}"')
            self._writeln(f'\t@printf "  {rule_pfx}\x1b[32;01m{rule: <35}\x1b[0m {desc2}{bslash}n"')
        self._writeln(f'\t@printf "{bslash}n"')

    # --------------------
    ## generate lines to clean all generated files
    #
    # @return None
    def _gen_clean(self):
        rule = 'clean'
        clean_tgts = ''
        for tgt in self._targets:
            clean_tgts += f'{tgt.target}-clean '

        self._gen_rule(rule, clean_tgts, 'clean files')
        self._writeln('')

    # --------------------
    ## write a line to the makefile
    #
    # @param line  the line to write
    # @return None
    def _writeln(self, line):
        self._fp.write(line + '\n')

    # --------------------
    ## add a line for target help
    #
    # @param target   the target
    # @param desc     the help line
    # @return None
    def _add_help(self, target, desc):
        # TODO duplicate of function in target_base
        if target in self._help:
            svc.log.warn(f'add_help: target "{target}" already has description')
            svc.log.warn(f'   prev: {self._help[target]}')
            svc.log.warn(f'   curr: {desc}')
            svc.log.warn('   replacing...')
        self._help[target] = desc

    # --------------------
    ## generate a rule
    #
    # @param rule   the rule to generate
    # @param deps   the dependencies for this rule
    # @param desc   the help line
    # @return None
    def _gen_rule(self, rule, deps, desc):
        self._writeln(f'#-- {desc}')
        self._add_help(rule, desc)
        if deps:
            self._writeln(f'{rule}: {deps}')
        else:
            self._writeln(f'{rule}:')

    # --------------------
    ## generate root Makefile. This includes the correct file for the current OS
    #
    # @return None
    def _gen_root_makefile(self):
        content = ''
        content += '.phony: current_os\n'
        content += 'ifeq ($(OS),Windows_NT)\n'
        content += '    OS_NAME := $(shell  c:/msys64/usr/bin/uname.exe -s)\n'
        content += '    ifeq ($(findstring MINGW64,$(OS_NAME)),MINGW64)\n'
        content += '        PLATFORM := msys2\n'
        content += '        include Makefile.win\n'
        content += '    else ifeq ($(findstring MSYS,$(OS_NAME)),MSYS)\n'
        content += '        # for CLion\n'
        content += '        PLATFORM := msys2\n'
        content += '        include Makefile.win\n'
        content += '    else\n'
        content += '        # Handle other operating systems or raise an error\n'
        content += '        $(error Unsupported windows OS: "$(OS_NAME)")\n'
        content += '        $(error select one of: Linux, Darwin, MINGW64)\n'
        content += '    endif\n'
        content += 'else\n'
        content += '    OS_NAME := $(shell uname -s)\n'
        content += '    ifeq ($(OS_NAME),Linux)\n'
        content += '        PLATFORM := ubuntu\n'
        content += '        include Makefile.ubuntu\n'
        content += '    else ifeq ($(OS_NAME),Darwin)\n'
        content += '        PLATFORM := macos\n'
        content += '        include Makefile.macos\n'
        content += '    else\n'
        content += '        # Handle other operating systems or raise an error\n'
        content += '        $(error Unsupported OS: "$(OS_NAME)")\n'
        content += '        $(error select one of: Linux, Darwin, MINGW64)\n'
        content += '    endif\n'
        content += 'endif\n'
        content += '\n'
        content += 'current_os:\n'
        content += '\t@echo "Current platform:$(PLATFORM), uname:$(OS_NAME), OS:$(OS)"\n'
        path = 'Makefile'
        svc.log.highlight('generating root Makefile...')
        with open(path, 'w', encoding='utf-8', newline='\n') as self._fp:
            self._fp.write(content)
