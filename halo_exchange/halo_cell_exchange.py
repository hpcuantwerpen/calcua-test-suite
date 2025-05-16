# Copyright 2016-2021 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.backends import getlauncher


class HaloCellExchangeTest(rfm.RegressionTest):
    def __init__(self):
        self.sourcepath = 'halo_cell_exchange.c'
        self.build_system = 'SingleSource'
        self.build_system.cflags = ['-O2']
        self.valid_systems = ['+default']
        self.valid_prog_environs = ['+mpi']
        self.executable_opts = ['input.txt']

        self.sanity_patterns = sn.assert_eq(
            sn.count(sn.findall(r'halo_cell_exchange', self.stdout)), 9)

        self.perf_patterns = {
            'time_2_10': sn.extractsingle(
                r'halo_cell_exchange [0-9]+ 2 1 1 10 10 10'
                r' \S+ (?P<time_mpi>\S+)', self.stdout,
                'time_mpi', float),
            'time_2_10000': sn.extractsingle(
                r'halo_cell_exchange [0-9]+ 2 1 1 10000 10000 10000'
                r' \S+ (?P<time_mpi>\S+)', self.stdout,
                'time_mpi', float),
            'time_2_1000000': sn.extractsingle(
                r'halo_cell_exchange [0-9]+ 2 1 1 1000000 1000000 1000000'
                r' \S+ (?P<time_mpi>\S+)', self.stdout,
                'time_mpi', float),
            'time_4_10': sn.extractsingle(
                r'halo_cell_exchange [0-9]+ 2 2 1 10 10 10'
                r' \S+ (?P<time_mpi>\S+)', self.stdout,
                'time_mpi', float),
            'time_4_10000': sn.extractsingle(
                r'halo_cell_exchange [0-9]+ 2 2 1 10000 10000 10000'
                r' \S+ (?P<time_mpi>\S+)', self.stdout,
                'time_mpi', float),
            'time_4_1000000': sn.extractsingle(
                r'halo_cell_exchange [0-9]+ 2 2 1 1000000 1000000 1000000'
                r' \S+ (?P<time_mpi>\S+)', self.stdout,
                'time_mpi', float),
            'time_6_10': sn.extractsingle(
                r'halo_cell_exchange [0-9]+ 3 2 1 10 10 10'
                r' \S+ (?P<time_mpi>\S+)', self.stdout,
                'time_mpi', float),
            'time_6_10000': sn.extractsingle(
                r'halo_cell_exchange [0-9]+ 3 2 1 10000 10000 10000'
                r' \S+ (?P<time_mpi>\S+)', self.stdout,
                'time_mpi', float),
            'time_6_1000000': sn.extractsingle(
                r'halo_cell_exchange [0-9]+ 3 2 1 1000000 1000000 1000000'
                r' \S+ (?P<time_mpi>\S+)', self.stdout,
                'time_mpi', float)
        }
        self.maintainers = ['Michele Pugno']
        self.tags = {'halo', 'calcua', 'compilation', 'performance', 'daily'}


@rfm.simple_test
class HaloCellExchange(HaloCellExchangeTest):
    def __init__(self):
        super().__init__()

    @run_before('run')
    def set_num_cpus(self):
        self.num_tasks_per_node = self.current_partition.extras['num_cpus']
        self.num_tasks = self.num_tasks_per_node * 2


    @run_before('run')
    def set_details(self):
        self.job.options = ['--time 00:20:00', '--exclusive', '--switches=1']

    @run_before('run')
    def set_launcher(self):
        self.job.launcher = getlauncher('srun')()
