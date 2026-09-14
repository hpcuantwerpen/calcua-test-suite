# Copyright 2016-2021 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class AllocSpeedTest(rfm.RegressionTest):
    valid_systems = ['-gpu']
    valid_prog_environs = ['standard']
    descr = 'Time to allocate 8192 MB'
    tags = {'calcua', 'performance', 'compilation', 'alloc'}
    maintainers = ['Michele Pugno']

    def __init__(self):
        self.sourcepath = 'alloc_speed.cpp'
        self.build_system = 'SingleSource'
        self.build_system.cxxflags = ['-O3', '-std=c++11']

        self.sanity_patterns = sn.assert_found('4096 MB', self.stdout)
        self.perf_patterns = {
            'time': sn.extractsingle(r'8192 MB, allocation time (?P<time>\S+)',
                                     self.stdout, 'time', float)
        }

    @run_before('run')
    def set_memory_limit(self):
        self.job.options = ['--mem=20g']