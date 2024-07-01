# Copyright 2016-2021 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class FFTWTest(rfm.RegressionTest):
    valid_systems = ['*:mpi-job']
    valid_prog_environs = ['foss-2021a', 'intel-2021a']
    sourcepath = 'fftw_benchmark.c'
    build_system = 'SingleSource'
    
    flags = variable(dict, value={
        'foss-2021a':   ['-O2', '-lfftw3'],
        'intel-2021a': ['-O2', '-mkl']
    })
    tags = {'calcua', 'performance', 'compilation', 'fftw'}

    def __init__(self):
        self.reference = {
        'leibniz:mpi-job': {'fftw_exec_time': (12, None, 0.10, 'seconds')},
        'breniac:mpi-job': {'fftw_exec_time': (12, None, 0.10, 'seconds')},
        'vaughan:mpi-job': {'fftw_exec_time': (12, None, 0.10, 'seconds')},
        }
        self.sanity_patterns = sn.assert_eq(
            sn.count(sn.findall(r'execution time', 'fftw.out')), 1)
        
        self.perf_patterns = {
            'fftw_exec_time': sn.extractsingle(
                r'execution time:\s+(?P<exec_time>\S+)', 'fftw.out',
                'exec_time', float),
        }

        if self.current_system.name in ['leibniz', 'breniac']:
            self.num_tasks = 56
            self.num_tasks_per_node = 28
            self.executable_opts = ['224 56 1000 1 >fftw.out']
        elif self.current_system.name in ['vaughan']:
            self.num_tasks = 128
            self.num_tasks_per_node = 64
            self.executable_opts = ['224 128 1000 1 >fftw.out']

    @run_before('compile')
    def set_compiler_flags(self):
        environ = self.current_environ.name
        self.build_system.cflags = self.flags.get(environ, [])

    @run_before('run')
    def set_details(self):
        self.job.options = ['--time 00:20:00', '--exclusive', '--switches=1']

    # @run_after('setup')
    # def set_reference(self):
    #     envname = self.current_environ.name
    #     system = self.current_system.name
    #     partition = self.current_partition.name
    #     value = self.par_references[partition][envname]
    #     reference = system + ':' + partition

    #     self.reference = {
    #         reference: {
    #             'fftw_exec_time': (value, None, 0.05, 's'),
    #         },
    #     }
