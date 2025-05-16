import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.builtins import *
import os
from reframe.core.backends import getlauncher

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
    valid_systems = ['+default']
    version = parameter(['VASP/6.5.1-intel-2024a-Wannier90-3.1.0-HDF5-1.14.5-DFTD4-3.7.0', 'VASP/6.4.2-intel-2022a-vtst-199-Wannier90-3.1.0-HDF5-1.12.2'])
    valid_prog_environs = ['standard']
    executable = 'vasp_std'
    tags = {'calcua', 'performance', 'vasp'}
    num_nodes = parameter([4, 10])
    time_limit = '1h'

    @run_before('run')
    def setup_run(self):
        self.num_tasks_per_node = self.current_partition.extras['num_cpus']
        self.num_tasks = self.num_nodes * self.num_tasks_per_node

    @run_before('run')
    def replace_launcher(self):
        self.job.launcher = getlauncher('srun')()

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
        self.modules = [self.version]
        self.job.options = ['--time 01:00:00', '--switches=1', '--exclusive']
