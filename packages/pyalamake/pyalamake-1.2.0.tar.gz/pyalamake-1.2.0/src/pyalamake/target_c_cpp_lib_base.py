from .svc import svc
from .target_base import TargetBase


# --------------------
## generate a C++ Library target, static (default) or shared
# see https://renenyffenegger.ch/notes/development/languages/C-C-plus-plus/GCC/create-libraries/index
class TargetCCppLibBase(TargetBase):
    # create() is c/c++ specific

    # --------------------
    ## constructor
    #
    # @param target_name  the name of this target
    def __init__(self, target_name):
        super().__init__(target_name)

        ## the C/C++ lib target type
        self._target_type = 'unset'
        ## list of object files
        self._objs = ''
        ## compiler to use
        self._cxx = 'unset'
        ## list of compile options
        self.add_compile_options('-D_GNU_SOURCE')  # pylint: disable=E1101

        ## list of build directories
        self._build_dirs = {}

        ## library type: static, shared
        self._lib_type = 'static'

    # target_type() is c/c++ specific
    # compiler() getter/setter are c/c++ specific

    # --------------------
    ## set the library type to generate
    #
    # @param val  the type to set: static or shared
    def set_type(self, val):
        valid_types = ['static', 'shared']
        if val not in valid_types:
            svc.abort(f'invalid library type, expected {valid_types}, actual: {val}')
        self._lib_type = val

    # --------------------
    ## check target for any issues
    #
    # @return None
    def check(self):
        svc.log.highlight(f'{self.target}: check target...')
        self._common_check()

    # --------------------
    ## gen C++ library target
    #
    # @return None
    def gen_target(self):
        svc.log.highlight(f'{self.target}: gen target, type:{self._target_type}')

        self._gen_args()
        self._gen_init()
        self._gen_lib()
        if self._lib_type == 'shared':
            self._gen_shared_library()
        else:
            self._gen_static_library()

    # --------------------
    ## create output directory
    #
    # @return None
    def _gen_args(self):
        # create output build directory
        self._build_dirs[svc.gbl.build_dir] = 1

        for file in self.sources:  # pylint: disable=E1101
            _, _, dst_dir = self._get_obj_path(file)
            self._build_dirs[dst_dir] = 1

        self._writeln('')

    # --------------------
    ## gen initial content for C++ library
    #
    # @return None
    def _gen_init(self):
        rule = f'{self.target}-init'
        self.add_rule(rule)

        self._gen_rule(rule, '', f'{self.target}: initialize for {svc.gbl.build_dir} build')
        for bld_dir in self._build_dirs:
            self._writeln(f'\t@mkdir -p {svc.osal.fix_path(bld_dir)}')
        self._writeln('')

    # --------------------
    ## gen lib build target
    #
    # @return None
    def _gen_lib(self):
        rule = f'{self.target}-build'
        self.add_rule(rule)

        build_deps = ''
        for src_file in self.sources:  # pylint: disable=E1101
            obj, mmd_inc, dst_dir = self._get_obj_path(src_file)

            # gen clean paths
            clean_path = dst_dir.replace(f'{svc.gbl.build_dir}/', '')
            self.add_clean(f'{svc.osal.fix_path(clean_path)}/*.o')
            self.add_clean(f'{svc.osal.fix_path(clean_path)}/*.d')

            self._writeln(f'-include {svc.osal.fix_path(mmd_inc)}')
            self._writeln(f'{svc.osal.fix_path(obj)}: {svc.osal.fix_path_win(src_file)}')
            fpic = ''
            if self._lib_type == 'shared':
                fpic = '-fPIC '
            self._writeln(f'\t{self._cxx} -MMD {fpic} -c {self._inc_dirs} {self._compile_opts} '
                          f'{svc.osal.fix_path_win(src_file)} -o {svc.osal.fix_path(obj)}')
            self._objs += f'{svc.osal.fix_path(obj)} '
            build_deps += f'{svc.osal.fix_path(src_file)} '

        self._writeln('')

        self._gen_rule(rule, self._objs, f'{self.target}: build source files')
        self._writeln('')

    # --------------------
    ## gen shared library
    #
    # @return None
    def _gen_shared_library(self):
        rule = f'{self.target}-shared'
        self.add_rule(rule)

        if svc.gbl.os_name == 'win':
            extension = 'dll'
        else:
            extension = 'so'
        lib_name = f'lib{self.target}.{extension}'
        lib = f'{svc.gbl.build_dir}/{lib_name}'
        self._writeln(f'{svc.osal.fix_path(lib)}: {self._objs}')
        self._writeln(f'\t{self._cxx} -MMD --shared -fPIC {self._objs} {self._link_opts} {self._link_paths} '
                      f'{self._libs} '
                      f'-o {svc.osal.fix_path(lib)}')
        self._writeln('')
        ## see baseclass for definition of self.target
        self.add_clean(lib_name)

        self._gen_rule(rule, lib, f'{self.target}: link')
        self._writeln('')

    # --------------------
    ## gen static library
    #
    # @return None
    def _gen_static_library(self):
        rule = f'{self.target}-shared'
        self.add_rule(rule)

        lib_name = f'lib{self.target}.a'
        lib = f'{svc.gbl.build_dir}/{lib_name}'
        self._writeln(f'{svc.osal.fix_path(lib)}: {self._objs}')
        self._writeln(
            f'\tar rcs {svc.osal.fix_path(lib)} {self._objs} {self._link_opts} {self._link_paths} {self._libs}')
        self._writeln('')
        ## see baseclass for definition of self.target
        self.add_clean(lib_name)

        self._gen_rule(rule, lib, f'{self.target}: link')
        self._writeln('')
