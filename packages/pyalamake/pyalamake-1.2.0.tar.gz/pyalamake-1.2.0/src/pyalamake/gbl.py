import os
import sys


# --------------------
## holds global information
class Gbl:
    ## hold the name of the build directory; default is debug
    build_dir = 'debug'
    ## holds the current OS name
    os_name = 'unknown'

    ## only do this once in cpp/gtest
    genned_empty_rule = False

    ## set clean commands to be quiet (prefix with '@')
    quiet_clean = False
    ## generate the compile_commands.json file
    gen_compile_commands = True

    # --------------------
    ## constructor
    def __init__(self):
        ## holds the current OS name
        self.os_name = 'unknown'
        # NOTE: has to use os.path.isfile here since the current OS is unknown
        if os.path.isfile('/sys/firmware/devicetree/base/model'):
            self.os_name = 'rpi'
        elif sys.platform == 'win32':
            self.os_name = 'win'
        elif sys.platform == 'darwin':
            self.os_name = 'macos'
        elif sys.platform == 'linux':
            self.os_name = 'ubuntu'
        else:
            print(f'unrecognized OS: "{sys.platform}"')

    # --------------------
    ## override the default build directory name
    #
    # @param build_dir  the new build directory
    # @return None
    def set_build_dir(self, build_dir):
        ## see Gbl.build_dir
        self.build_dir = build_dir
