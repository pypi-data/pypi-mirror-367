import json
import os
import re
import subprocess
from abc import ABC, abstractmethod

from .svc import svc


# --------------------
## base class to ensure both Null and real classes match up for function signatures
class CompileCmdJsonBase(ABC):
    # --------------------
    ## (skipped) initializer
    @abstractmethod
    def init(self):
        pass

    # --------------------
    ## (skipped) get info
    # @param line   (not used)
    @abstractmethod
    def get_info(self, line):
        pass

    # --------------------
    ## (skipped) save file
    @abstractmethod
    def save(self):
        pass


# --------------------
## return the correct class based on the configuration selected by the user
# use CamelCase to make it look like a class instantiation
# noinspection PyPep8Naming
def CompileCmdJson():  # pylint: disable=invalid-name
    if svc.gbl.gen_compile_commands:
        # generate the json file
        return _CompileCmdJson()

    # do not generate json file
    return _CompileCmdJsonNone()


# --------------------
## Null version of CompileCmdJson; used to skip generation of file
class _CompileCmdJsonNone(CompileCmdJsonBase):
    # --------------------
    ## (skipped) initializer
    def init(self):
        # TODO should this delete any existing compile_commands.json?
        pass

    # --------------------
    ## (skipped) get info
    # @param line   (not used)
    def get_info(self, line):
        pass

    # --------------------
    ## (skipped) save file
    def save(self):
        pass


# --------------------
## generate compile_commands.json file for clang-tidy linter
class _CompileCmdJson(CompileCmdJsonBase):
    # --------------------
    ## constructor
    def __init__(self):
        ## found a valid makefile line to parse or not
        self._found_it = False
        ## how many non-system compile objects found
        self._count = 0
        ## list of compile commands found
        self._compile_cmds = []
        ## info about the current command
        self._curr_cmd = {}

    # --------------------
    ## initialize
    def init(self):
        self._found_it = False

    # --------------------
    ## get information from the given makefile line
    #
    # @param line   the makefile line
    # @return None
    def get_info(self, line):
        if self._found_it:
            self._handle_line2(line)
            self._found_it = False
            self._curr_cmd = {}
            return

        m = re.search(r'(.*\.o):\s+(.*)', line)
        if not m:
            return

        obj_file = m.group(1)
        src_file = m.group(2)
        if src_file.startswith('/usr'):
            # exclude system includes/files
            return

        self._count += 1
        self._curr_cmd = {}
        self._compile_cmds.append(self._curr_cmd)
        self._handle_line1(obj_file, src_file)
        self._found_it = True

    # --------------------
    ## save the information to the compile_commands.json file
    #
    # @return None
    def save(self):
        # print(f'@@ DBG found: {self._count}')
        with open('compile_commands.json', 'w', encoding='utf-8', newline='\n') as fp:
            json.dump(self._compile_cmds, fp, indent=2, sort_keys=True)

    # --------------------
    ## get info from the first line of output
    #
    # @param obj_file  the obj file name
    # @param src_file  the src file name
    # @return None
    def _handle_line1(self, obj_file, src_file):
        # print(f'@@ DBG line1 {self._count: >2}: {obj_file} {src_file}')
        root_path = os.getcwd()
        self._curr_cmd['directory'] = root_path
        if src_file.startswith('/'):
            self._curr_cmd['file'] = src_file
        else:
            self._curr_cmd['file'] = os.path.join(root_path, src_file)

        if obj_file.startswith('/'):
            self._curr_cmd['output'] = obj_file
        else:
            self._curr_cmd['output'] = os.path.join(root_path, obj_file)

    # --------------------
    ## get info from the second line of output
    #
    # @param line  the second line
    # @return None
    def _handle_line2(self, line):
        tokens = []
        for token in line.strip().split():
            token = token.strip('"')
            if token in ['-MMD']:
                continue

            if not tokens:
                # first token is the command
                token = self._get_full_path(token)

            tokens.append(token)
        # print(f'@@ DBG line2 {self._count: >2}: {tokens}')
        self._curr_cmd['arguments'] = tokens

    # --------------------
    ## get the full path to the given command name
    #
    # @param cmd  the command to get info about
    # @return None
    def _get_full_path(self, cmd):
        result = subprocess.run(f'which {cmd}',
                                shell=True,  # Execute via shell
                                capture_output=True,  # Capture stdout and stderr
                                text=True,  # Decode output as string
                                check=True)  # Raise error for non-zero exit codes
        return result.stdout.strip()
