# Copyright 2016-2021 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class AllocSpeedTest(rfm.RegressionTest):
    valid_systems = ['*:default-node']
    valid_prog_environs = ['standard']
    descr = 'Time to allocate 4096 MB'
    tags = {'calcua', 'performance', 'compilation'}
    reference = {
        'leibniz:default-node': {'time': (20.4154, None, 0.05, 'seconds')},
        'breniac:default-node': {'time': (20.4154, None, 0.05, 'seconds')},
        'vaughan:default-node': {'time': (20.4154, None, 0.05, 'seconds')},
        }
    
    def __init__(self):
        self.sourcepath = 'alloc_speed.cpp'
        self.build_system = 'SingleSource'
        self.build_system.cxxflags = ['-O3', '-std=c++11']
        self.tags = {'calcua', 'performance', 'compilation', 'alloc'}

        self.sanity_patterns = sn.assert_found('4096 MB', self.stdout)
        self.perf_patterns = {
            'time': sn.extractsingle(r'8192 MB, allocation time (?P<time>\S+)',
                                     self.stdout, 'time', float)
        }
        self.maintainers = ['Michele Pugno']

    # @run_before('performance')
    # def set_reference(self):
    #     self.reference = self.env_reference[self.current_environ.name]

    @run_before('run')
    def set_memory_limit(self):
        if self.current_system.name != "leibniz":
            self.job.options = ['--mem=20g']