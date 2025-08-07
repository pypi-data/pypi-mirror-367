from .svc import svc
from .target_c_cpp_lib_base import TargetCCppLibBase


# --------------------
## generate a C Library target, static (default) or shared
class TargetCLib(TargetCCppLibBase):
    # --------------------
    ## create a C++ library instance
    #
    # @param targets      current list of targets
    # @param target_name  name of new target to add
    @classmethod
    def create(cls, targets, target_name):
        impl = TargetCLib(target_name)
        targets.append(impl)
        return impl

    # --------------------
    ## constructor
    #
    # @param target_name  the name of this target
    def __init__(self, target_name):
        super().__init__(target_name)

        ## the C lib target type
        self._target_type = 'c-lib'
        ## list of object files
        self._objs = ''
        ## compiler to use
        self._cxx = svc.osal.c_compiler()
        ## list of compile options
        self.add_compile_options('-std=c17')  # pylint: disable=E1101

        ## list of build directories
        self._build_dirs = {}

        ## library type: static, shared
        self._lib_type = 'static'

    # --------------------
    ## return target type
    #
    # @return cpp target
    @property
    def target_type(self):
        return self._target_type

    # --------------------
    ## return compiler to use
    # @return compiler to use
    @property
    def compiler(self):
        return self._cxx

    # --------------------
    ## set compiler to use
    # @param val  the compiler setting
    # @return None
    @compiler.setter
    def compiler(self, val):
        self._cxx = val
        # not needed, but adding anyway
        self._compile_opts_param.remove('-std=c++20')  # pylint: disable=E1101
