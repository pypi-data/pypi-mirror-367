from .svc import svc
from .target_c_cpp_base import TargetCCppBase


# --------------------
## generate a C target
class TargetC(TargetCCppBase):
    # --------------------
    ## create a C++ target instance
    #
    # @param targets      current list of targets
    # @param target_name  name of new target to add
    @classmethod
    def create(cls, targets, target_name):
        impl = TargetC(target_name)
        targets.append(impl)
        return impl

    # --------------------
    ## constructor
    #
    # @param target_name  the name of this target
    def __init__(self, target_name):
        super().__init__(target_name)

        ## the C target type
        self._target_type = 'c'
        ## list of object files
        self._objs = ''
        ## compiler to use
        self._cxx = svc.osal.c_compiler()
        ## list of compile options
        self.add_compile_options('-std=c17')  # pylint: disable=E1101

        ## list of build directories
        self._build_dirs = {}

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
        self._compile_opts_param.remove('-std=c++20')
