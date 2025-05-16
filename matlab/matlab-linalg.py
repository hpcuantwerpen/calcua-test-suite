# Copyright 2016-2021 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


class MatlabLinalgBaseTest(rfm.RunOnlyRegressionTest):
    def __init__(self):
        self.valid_prog_environs = ['standard']
        self.modules = ['MATLAB']

        self.perf_patterns = {
            'dot': sn.extractsingle(
                r'Dot product:\s+(?P<dot>\S+)\s+s',
                self.stdout, 'dot', float),
            'cholesky': sn.extractsingle(
                r'Cholesky factorisation:'
                r'\s+(?P<cholesky>\S+)\s+s',
                self.stdout, 'cholesky', float),
            'lu': sn.extractsingle(
                r'LU factorisation:'
                r'\s+(?P<lu>\S+)\s+s',
                self.stdout, 'lu', float),
        }
        self.sanity_patterns = sn.assert_found(r'MATLAB Version: *',
                                               self.stdout)
        self.executable = 'cat'
        self.executable_opts = ['linalg.m | matlab -nodesktop -nosplash']
        self.num_tasks_per_node = 1
        self.tags = {'apps', 'matlab', 'performance', 'vsc'}
        self.maintainers = ['Lewih']
        self.descr = 'Test a few typical Matlab operations'


@rfm.simple_test
class MatlabLinalgTest(MatlabLinalgBaseTest):
    def __init__(self):
        super().__init__()
        self.valid_systems = ['+default']

    @run_before('run')
    def setup_run(self):
        self.num_cpus_per_task = self.current_partition.extras['num_cpus']
        if self.num_cpus_per_task > 32:
              # do not use all 64 cores in vaughan
              self.num_cpus_per_task = 32
