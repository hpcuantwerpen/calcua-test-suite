# Copyright 2016-2021 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


class HaloCellExchangeTest(rfm.RegressionTest):
    def __init__(self):
        self.sourcepath = 'halo_cell_exchange.c'
        self.build_system = 'SingleSource'
        self.build_system.cflags = ['-O2']
        self.valid_systems = ['*:mpi-job']

        self.executable_opts = ['input.txt']

        self.sanity_patterns = sn.assert_eq(
            sn.count(sn.findall(r'halo_cell_exchange', self.stdout)), 9)

        self.perf_patterns = {
            'time_2_10': sn.extractsingle(
                r'halo_cell_exchange [0-9]{2} 2 1 1 10 10 10'
                r' \S+ (?P<time_mpi>\S+)', self.stdout,
                'time_mpi', float),
            'time_2_10000': sn.extractsingle(
                r'halo_cell_exchange [0-9]{2} 2 1 1 10000 10000 10000'
                r' \S+ (?P<time_mpi>\S+)', self.stdout,
                'time_mpi', float),
            'time_2_1000000': sn.extractsingle(
                r'halo_cell_exchange [0-9]{2} 2 1 1 1000000 1000000 1000000'
                r' \S+ (?P<time_mpi>\S+)', self.stdout,
                'time_mpi', float),
            'time_4_10': sn.extractsingle(
                r'halo_cell_exchange [0-9]{2} 2 2 1 10 10 10'
                r' \S+ (?P<time_mpi>\S+)', self.stdout,
                'time_mpi', float),
            'time_4_10000': sn.extractsingle(
                r'halo_cell_exchange [0-9]{2} 2 2 1 10000 10000 10000'
                r' \S+ (?P<time_mpi>\S+)', self.stdout,
                'time_mpi', float),
            'time_4_1000000': sn.extractsingle(
                r'halo_cell_exchange [0-9]{2} 2 2 1 1000000 1000000 1000000'
                r' \S+ (?P<time_mpi>\S+)', self.stdout,
                'time_mpi', float),
            'time_6_10': sn.extractsingle(
                r'halo_cell_exchange [0-9]{2} 3 2 1 10 10 10'
                r' \S+ (?P<time_mpi>\S+)', self.stdout,
                'time_mpi', float),
            'time_6_10000': sn.extractsingle(
                r'halo_cell_exchange [0-9]{2} 3 2 1 10000 10000 10000'
                r' \S+ (?P<time_mpi>\S+)', self.stdout,
                'time_mpi', float),
            'time_6_1000000': sn.extractsingle(
                r'halo_cell_exchange [0-9]{2} 3 2 1 1000000 1000000 1000000'
                r' \S+ (?P<time_mpi>\S+)', self.stdout,
                'time_mpi', float)
        }
        self.maintainers = ['Michele Pugno']
        self.tags = {'halo', 'calcua', 'compilation'}


@rfm.simple_test
class HaloCellExchange(HaloCellExchangeTest):
    def __init__(self):
        super().__init__()
        self.valid_prog_environs = ['foss-2021a', 'intel-2021a']

        self.reference = {
                'leibniz:mpi-job': {
                    'time_2_10': (3.570087e-06, None, 0.50, 's'),
                    'time_2_10000': (1.234696e-05, None, 0.50, 's'),
                    'time_2_1000000': (0.001060408, None, 0.50, 's'),
                    'time_4_10': (3.119417e-06, None, 0.50, 's'),
                    'time_4_10000': (1.31086e-05, None, 0.50, 's'),
                    'time_4_1000000': (0.002062185, None, 0.50, 's'),
                    'time_6_10': (3.214831e-06, None, 0.50, 's'),
                    'time_6_10000': (1.410393e-05, None, 0.50, 's'),
                    'time_6_1000000': (0.002393336, None, 0.50, 's')
                },
                'breniac:mpi-job': {
                    'time_2_10': (3.570087e-06, None, 0.50, 's'),
                    'time_2_10000': (1.234696e-05, None, 0.50, 's'),
                    'time_2_1000000': (0.001060408, None, 0.50, 's'),
                    'time_4_10': (3.119417e-06, None, 0.50, 's'),
                    'time_4_10000': (1.31086e-05, None, 0.50, 's'),
                    'time_4_1000000': (0.002062185, None, 0.50, 's'),
                    'time_6_10': (3.214831e-06, None, 0.50, 's'),
                    'time_6_10000': (1.410393e-05, None, 0.50, 's'),
                    'time_6_1000000': (0.002393336, None, 0.50, 's')
                },
                'vaughan:mpi-job': {
                    'time_2_10': (3.006092e-06, None, 0.50, 's'),
                    'time_2_10000': (7.754467e-06, None, 0.50, 's'),
                    'time_2_1000000': (0.001442269, None, 0.50, 's'),
                    'time_4_10': (3.219354e-06, None, 0.50, 's'),
                    'time_4_10000': (8.425722e-06, None, 0.50, 's'),
                    'time_4_1000000': (0.003161711, None, 0.50, 's'),
                    'time_6_10': (3.964607e-06, None, 0.50, 's'),
                    'time_6_10000': (1.101113e-05, None, 0.50, 's'),
                    'time_6_1000000': (0.004619305 , None, 0.50, 's')
                },
        }

    # @run_before('performance')
    # def set_reference(self):
    #     self.reference = self.env_reference[self.current_environ.name]

    @run_after('setup')
    def set_num_cpus(self):
        if self.current_system.name in ['leibniz', 'breniac']:
            self.num_tasks_per_node = 28
            self.num_tasks = 56
        else:
            self.num_tasks_per_node = 64
            self.num_tasks = 128

    @run_before('run')
    def set_details(self):
        self.job.options = ['--time 00:20:00', '--exclusive', '--switches=1']
