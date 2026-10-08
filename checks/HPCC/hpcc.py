import os

import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.backends import getlauncher    

# Upstream HPCC has no release after 1.5.0 (2016). This commit (2022-12-12) is the last code
# change: it adds FFTW3 support and builds with MPI-3 implementations such as Open MPI 5.
HPCC_COMMIT = 'd2b9a19b4498fdced2860f3394c03f27714b6160'
HPCC_URL = f'https://github.com/icl-utk-edu/hpcc/archive/{HPCC_COMMIT}.tar.gz'

# hpl/Make.calcua, after upstream's hpl/setup/Make.Linux-x86_64-OpenBLAS-FFTW3
MAKE_ARCH = '''\
SHELL        = /bin/sh
CD           = cd
CP           = cp
LN_S         = ln -s
MKDIR        = mkdir
RM           = /bin/rm -f
TOUCH        = touch
ARCH         = $(arch)
TOPdir       = ../../..
INCdir       = $(TOPdir)/include
BINdir       = $(TOPdir)/bin/$(ARCH)
LIBdir       = $(TOPdir)/lib/$(ARCH)
HPLlib       = $(LIBdir)/libhpl.a
MPdir        =
MPinc        =
MPlib        =
LAdir        =
LAinc        = {lainc}
LAlib        = {lalib}
F2CDEFS      = -DAdd_ -DF77_INTEGER=int -DStringSunStyle
HPL_INCLUDES = -I$(INCdir) -I$(INCdir)/$(ARCH) $(LAinc) $(MPinc)
HPL_LIBS     = $(HPLlib) $(LAlib) $(MPlib) -lm
HPL_OPTS     =
HPL_DEFS     = $(F2CDEFS) $(HPL_OPTS) $(HPL_INCLUDES)
CC           = {cc}
CCNOOPT      = $(HPL_DEFS)
CCFLAGS      = $(HPL_DEFS) {ccflags}
LINKER       = $(CC)
LINKFLAGS    = $(CCFLAGS)
ARCHIVER     = ar
ARFLAGS      = r
RANLIB       = echo
'''


class HPCCBuild(rfm.CompileOnlyRegressionTest):
    '''Download HPCC at HPCC_COMMIT and build it with the current toolchain (on the login node).'''
    valid_systems = ['*']
    valid_prog_environs = ['*']
    sourcesdir = None
    build_system = 'CustomBuild'
    # Per toolchain family, matched on the environment name ('foss-2025a_mpi' -> 'foss'); the
    # compiler comes from the environment in calcua_config.py. foss: FFTW3 (FFTW.MPI ships with
    # foss). intel: HPCC's built-in FFTE, since MKL has no ready-made FFTW3 MPI library. AVX2 for
    # broadwell/zen; GCC 14 and icx turn old C idioms in HPCC into errors, hence -fpermissive /
    # -Wno-error=...
    toolchains = variable(dict, value={
        'foss': {
            'ccflags': '-O3 -march=x86-64-v3 -fcommon -fpermissive',
            'lainc': '-DUSING_FFTW3',
            'lalib': '-lfftw3_mpi -lfftw3 -lflexiblas',
        },
        'intel': {
            'ccflags': '-O3 -march=core-avx2 -fcommon -Wno-error=implicit-function-declaration '
                       '-Wno-error=incompatible-function-pointer-types -Wno-error=int-conversion',
            'lainc': '',
            'lalib': '-qmkl=sequential',
        },
    })

    @run_before('compile')
    def prepare_build(self):
        env = self.current_environ
        self.skip_if('mpi' not in env.features, f'{env.name} has no MPI compiler wrappers')
        family = env.name.split('-')[0]
        tc = self.toolchains.get(family)
        self.skip_if(tc is None, f'no HPCC build settings for toolchain family {family!r} ({env.name})')
        with open(os.path.join(self.stagedir, 'Make.calcua'), 'w') as f:
            f.write(MAKE_ARCH.format(cc=env.cc, **tc))
        self.build_system.commands = [
            f'curl -sfL {HPCC_URL} | tar xz --strip-components=1',
            'cp Make.calcua hpl/',
            'make arch=calcua',
        ]

    @sanity_function
    def built(self):
        return sn.path_isfile(os.path.join(self.stagedir, 'hpcc'))


@rfm.simple_test
class HPCCTest(rfm.RunOnlyRegressionTest):
    num_nodes = parameter([1, 8, 24], type=int)
    tags = {'hpcc', 'calcua', 'compilation', 'performance'}
    # class-level so that -S valid_systems/valid_prog_environs=... can override them
    valid_systems = ['leibniz:broadwell', 'vaughan:zen2', 'vaughan:zen3', 'breniac:skylake']
    valid_prog_environs = ['foss-2025a_mpi', 'intel-2025a_mpi']
    hpcc = fixture(HPCCBuild, scope='environment')
    maintainers = ['Michele Pugno']

    def __init__(self):
        self.postrun_cmds = ['sleep 10'] # let's wait for scratch fs
        if int(self.num_nodes) > 8:
            self.tags.add('massive')

        self.sanity_patterns = sn.all([
            sn.assert_found(r'End of HPC Challenge tests.',
                            f'HPCC_{self.num_nodes}/hpccoutf.txt'),
            sn.assert_found(r'Command Executed. End.',
                            self.stdout)
        ])
        self.perf_patterns = {
            'HPL_Tflops': sn.extractsingle(r'HPL_Tflops=(?P<data>\S+)',
                                           f'HPCC_{self.num_nodes}/hpccoutf.txt',
                                           'data', float),
            'PTRANS_GBs': sn.extractsingle(r'PTRANS_GBs=(?P<data>\S+)',
                                           f'HPCC_{self.num_nodes}/hpccoutf.txt',
                                           'data', float),
            'MPIRandomAccess_GUPs': sn.extractsingle(r'MPIRandomAccess_GUPs=(?P<data>\S+)',
                                           f'HPCC_{self.num_nodes}/hpccoutf.txt',
                                           'data', float),
            'MPIFFT_Gflops': sn.extractsingle(r'MPIFFT_Gflops=(?P<data>\S+)',
                                           f'HPCC_{self.num_nodes}/hpccoutf.txt',
                                           'data', float),
            'StarSTREAM_Triad': sn.extractsingle(r'StarSTREAM_Triad=(?P<data>\S+)',
                                           f'HPCC_{self.num_nodes}/hpccoutf.txt',
                                           'data', float),
            'StarDGEMM_Gflops': sn.extractsingle(r'StarDGEMM_Gflops=(?P<data>\S+)',
                                           f'HPCC_{self.num_nodes}/hpccoutf.txt',
                                           'data', float), 
            'RandomlyOrderedRingBandwidth_GBytes': sn.extractsingle(r'RandomlyOrderedRingBandwidth_GBytes=(?P<data>\S+)',
                                           f'HPCC_{self.num_nodes}/hpccoutf.txt',
                                           'data', float), 
            'RandomlyOrderedRingLatency_usec': sn.extractsingle(r'RandomlyOrderedRingLatency_usec=(?P<data>\S+)',
                                           f'HPCC_{self.num_nodes}/hpccoutf.txt',
                                           'data', float), 
        }

    @run_before('run')
    def set_details(self):
        self.job.options = ['--time 06:00:00', '--switches=1']

    @run_after('setup')
    def skip_too_large(self):
        # skip massive on breniac
        self.skip_if(self.current_system.name == 'breniac' and self.num_nodes > 8,
                     f'{self.num_nodes} nodes is more than breniac can provide')

    @run_after('setup')
    def set_num_cpus(self):
        self.executable = './hpcc.sh'
        self.env_vars['HPCC_BIN'] = os.path.join(self.hpcc.stagedir, 'hpcc')
        self.num_tasks_per_node = self.current_partition.extras['num_cpus']
        self.num_tasks = self.num_tasks_per_node * int(self.num_nodes)

    @run_before('run')
    def replace_launcher(self):
        self.job.launcher = getlauncher('local')()
    