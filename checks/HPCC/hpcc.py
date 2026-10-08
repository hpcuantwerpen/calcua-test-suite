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
    # Per toolchain. foss: FFTW3 (FFTW.MPI ships with foss). intel: HPCC's built-in FFTE, since
    # MKL has no ready-made FFTW3 MPI library. AVX2 for broadwell/zen; GCC 14 and icx turn old C
    # idioms in HPCC into errors, hence -fpermissive / -Wno-error=...
    toolchains = variable(dict, value={
        'foss-2025a_mpi': {
            'cc': 'mpicc',
            'ccflags': '-O3 -march=x86-64-v3 -fcommon -fpermissive',
            'lainc': '-DUSING_FFTW3',
            'lalib': '-lfftw3_mpi -lfftw3 -lflexiblas',
        },
        'intel-2025a_mpi': {
            'cc': 'mpiicx',
            'ccflags': '-O3 -march=core-avx2 -fcommon -Wno-error=implicit-function-declaration '
                       '-Wno-error=incompatible-function-pointer-types -Wno-error=int-conversion',
            'lainc': '',
            'lalib': '-qmkl=sequential',
        },
    })

    @run_before('compile')
    def prepare_build(self):
        tc = self.toolchains.get(self.current_environ.name)
        self.skip_if(tc is None, f'no HPCC build settings for {self.current_environ.name}')
        with open(os.path.join(self.stagedir, 'Make.calcua'), 'w') as f:
            f.write(MAKE_ARCH.format(**tc))
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
    valid_systems = ['leibniz:broadwell', 'vaughan:zen2', 'vaughan:zen3']
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

        # self.num_nodes_reference = {
        #     '1':{
        #         'leibniz:default-node': {
        #             'HPL_Tflops': (0.892, -0.089, 0.089, 'Tflops'),
        #             'PTRANS_GBs': (9.34, -0.06, 0.06, 'GBs'),
        #             'MPIRandomAccess_GUPs': (0.405, -0.082, 0.082, 'GUPs'),
        #             'MPIFFT_Gflops': (33.34, -0.086, 0.086, 'Gflops'),
        #             'StarSTREAM_Triad': (4.60, -0.052, 0.052, 'Triad'),
        #             'StarDGEMM_Gflops': (35.98, -0.169, 0.169, 'Gflops'),
        #             'RandomlyOrderedRingBandwidth_GBytes': (0.966, -0.184, 0.184, 'GBs'),
        #             'RandomlyOrderedRingLatency_usec': (0.58, -0.1, 0.1, 'usec'),
        #         },
        #         'vaughan:default-node': {
        #             'HPL_Tflops': (1.84478, -0.1, 0.1, 'Tflops'),
        #             'PTRANS_GBs': (11.0, -0.1, 0.1, 'GBs'),
        #             'MPIRandomAccess_GUPs': (0.19, -0.1, 0.1, 'GUPs'),
        #             'MPIFFT_Gflops': (59.4144, -0.1, 0.1, 'Gflops'),
        #             'StarSTREAM_Triad': (4.27283, -0.01, 0.01, 'Triad'),
        #             'StarDGEMM_Gflops': (33.6247, -0.1, 0.1, 'Gflops'),
        #             'RandomlyOrderedRingBandwidth_GBytes': (0.525112, -0.1, 0.1, 'GBs'),
        #             'RandomlyOrderedRingLatency_usec': (1.04047, -0.1, 0.1, 'usec'),
        #         },
        #     },
        #     '2': {
        #         'leibniz:default-node': {
        #             'HPL_Tflops': (1.80669, -0.089, 0.089, 'Tflops'),
        #             'PTRANS_GBs': (15.5647, -0.06, 0.06, 'GBs'),
        #             'MPIRandomAccess_GUPs': (0.641649, -0.082, 0.082, 'GUPs'),
        #             'MPIFFT_Gflops': (49.7101, -0.086, 0.086, 'Gflops'),
        #             'StarSTREAM_Triad': (4.60, -0.052, 0.052, 'Triad'),
        #             'StarDGEMM_Gflops': (35.98, -0.169, 0.169, 'Gflops'),
        #             'RandomlyOrderedRingBandwidth_GBytes': (0.671674, -0.184, 0.184, 'GBs'),
        #             'RandomlyOrderedRingLatency_usec': (0.927608, -0.014, 0.014, 'usec'),
        #         },
        #         'vaughan:default-node': {
        #             'HPL_Tflops': (3.65754, -0.1, 0.1, 'Tflops'),
        #             'PTRANS_GBs': (13.6788, -0.1, 0.1, 'GBs'),
        #             'MPIRandomAccess_GUPs': (0.351861, -0.1, 0.1, 'GUPs'),
        #             'MPIFFT_Gflops': (41.8152, -0.1, 0.1, 'Gflops'),
        #             'StarSTREAM_Triad': (4.27457, -0.1, 0.1, 'Triad'),
        #             'StarDGEMM_Gflops': (33.4844, -0.1, 0.1, 'Gflops'),
        #             'RandomlyOrderedRingBandwidth_GBytes': (0.168236, -0.1, 0.1, 'GBs'),
        #             'RandomlyOrderedRingLatency_usec': (6.60655, -0.1, 0.1, 'usec'),
        #         },
        #     },
        #     '8': {
        #         'leibniz:default-node': {
        #             'HPL_Tflops': (7.0245, -0.089, 0.089, 'Tflops'),
        #             'PTRANS_GBs': (49.74705, -0.06, 0.06, 'GBs'),
        #             'MPIRandomAccess_GUPs': (1.875305, -0.082, 0.082, 'GUPs'),
        #             'MPIFFT_Gflops': (100.656, -0.086, 0.086, 'Gflops'),
        #             'StarSTREAM_Triad': (4.5237325, -0.052, 0.052, 'Triad'),
        #             'StarDGEMM_Gflops': (34.6867, -0.169, 0.169, 'Gflops'),
        #             'RandomlyOrderedRingBandwidth_GBytes': (0.33274825, -0.184, 0.184, 'GBs'),
        #             'RandomlyOrderedRingLatency_usec': (1.0244975, -0.014, 0.014, 'usec'),
        #         },
        #         'vaughan:default-node': {
        #             'HPL_Tflops': (14.5471 , -0.1, 0.1, 'Tflops'),
        #             'PTRANS_GBs': (34.2725, -0.1, 0.1, 'GBs'),
        #             'MPIRandomAccess_GUPs': (0.895806, -0.1, 0.1, 'GUPs'),
        #             'MPIFFT_Gflops': (103.021, -0.1, 0.1, 'Gflops'),
        #             'StarSTREAM_Triad': (4.27175, -0.1, 0.1, 'Triad'),
        #             'StarDGEMM_Gflops': (33.6372, -0.1, 0.1, 'Gflops'),
        #             'RandomlyOrderedRingBandwidth_GBytes': (0.100542, -0.1, 0.1, 'GBs'),
        #             'RandomlyOrderedRingLatency_usec': (15.638, -0.1, 0.1, 'usec'),
        #         },
        #     },
        #     '24': {
        #         'leibniz:default-node': {
        #             'HPL_Tflops': (20.38357, -0.089, 0.089, 'Tflops'),
        #             'PTRANS_GBs': (140.7002, -0.06, 0.06, 'GBs'),
        #             'MPIRandomAccess_GUPs': (4.06216, -0.082, 0.082, 'GUPs'),
        #             'MPIFFT_Gflops': (423.523, -0.086, 0.086, 'Gflops'),
        #             'StarSTREAM_Triad': (3.64279, -0.052, 0.052, 'Triad'),
        #             'StarDGEMM_Gflops': (34.6867, -0.169, 0.169, 'Gflops'),
        #             'RandomlyOrderedRingBandwidth_GBytes': (0.33274825, -0.184, 0.184, 'GBs'),
        #             'RandomlyOrderedRingLatency_usec': (1.104614, -0.014, 0.014, 'usec'),
        #         },
        #         'vaughan:default-node': {
        #             'HPL_Tflops': (41.2868 , -0.1, 0.1, 'Tflops'),
        #             'PTRANS_GBs': (88.147, -0.1, 0.1, 'GBs'),
        #             'MPIRandomAccess_GUPs': (2.41658, -0.1, 0.1, 'GUPs'),
        #             'MPIFFT_Gflops': (255.231, -0.1, 0.1, 'Gflops'),
        #             'StarSTREAM_Triad': (4.2694, -0.1, 0.1, 'Triad'),
        #             'StarDGEMM_Gflops': (33.5848 , -0.1, 0.1, 'Gflops'),
        #             'RandomlyOrderedRingBandwidth_GBytes': (0.0712722, -0.1, 0.1, 'GBs'),
        #             'RandomlyOrderedRingLatency_usec': (18.3818, -0.1, 0.1, 'usec'),
        #         },
        #     }
        # }

        #self.reference = self.num_nodes_reference[self.num_nodes]

    @run_before('run')
    def set_details(self):
        self.job.options = ['--time 06:00:00', '--switches=1']

    @run_after('setup')
    def set_num_cpus(self):
        self.executable = './hpcc.sh'
        self.env_vars['HPCC_BIN'] = os.path.join(self.hpcc.stagedir, 'hpcc')
        self.num_tasks_per_node = self.current_partition.extras['num_cpus']
        self.num_tasks = self.num_tasks_per_node * int(self.num_nodes)

    @run_before('run')
    def replace_launcher(self):
        self.job.launcher = getlauncher('local')()
    