import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.builtins import *
import os

INCAR_TEMPLATE = """SYSTEM=UO2
ALGO = Normal
ISMEAR = 0
SIGMA = 0.05
ISPIN = 2
ENCUT = 500
EDIFF = 1E-05
NCORE = 4
KPAR = {kpar}
"""

@rfm.simple_test
class vasp_test(rfm.RunOnlyRegressionTest):
    valid_systems = ['vaughan:mpi-job', 'leibniz:mpi-job']  # single-node = std node. mpi will be loaded with vasp module
    modules = ['VASP/6.4.2-intel-2022a-vtst-199-Wannier90-3.1.0-HDF5-1.12.2']  # full name of module unless (D)
    valid_prog_environs = ['*']  # standard, builtin also ok
    executable = 'vasp_std'
    tags = {'calcua', 'performance', 'vasp'}
    num_nodes = parameter([1, 2, 4, 10])
    # allref = {1: {'vaughan:mpi-job': {'elapsed_time': (1641, None, 0.1, 's')}},
    #           2: {'vaughan:mpi-job': {'elapsed_time': (839, None, 0.1, 's')}},
    #           4: {'vaughan:mpi-job': {'elapsed_time': (578, None, 0.1, 's')}},
    #           10: {'vaughan:mpi-job': {'elapsed_time': (307, None, 0.1, 's')}}}    # TODO add ref timings leibniz
    time_limit = '1h'

    @run_after('init')
    def setup_run(self):
        if self.current_system.name == 'vaughan':
            self.num_tasks_per_node = 64
        elif self.current_system.name in ['leibniz', 'breniac']:
            self.num_tasks_per_node = 28
        self.num_tasks = self.num_nodes * self.num_tasks_per_node
        #self.reference = self.allref[self.num_nodes]

    @run_after('setup')
    def write_incar(self):
        self.kpar = self.num_nodes

        inp_file = os.path.join(self.stagedir, 'INCAR')
        with open(inp_file, 'w', encoding='utf-8') as file:
            file.write(INCAR_TEMPLATE.format(kpar=self.kpar))

    @sanity_function
    def validate(self):
        sn_cores = sn.assert_found(rf'running\s+{self.num_tasks} mpi-ranks, on\s+{self.num_nodes} nodes',
                                   'OUTCAR')
        sn_brmix = sn.assert_not_found('BRMIX: very serious problems:', self.stdout)
        return sn_cores and sn_brmix

    @performance_function('s')
    def elapsed_time(self):
        return sn.extractsingle(r'Elapsed time \(sec\):\s+(?P<time>\S+)', 'OUTCAR', 'time', float)

    @run_before('run')
    def set_details(self):
        self.job.options = ['--time 01:00:00', '--switches=1', '--exclusive']

