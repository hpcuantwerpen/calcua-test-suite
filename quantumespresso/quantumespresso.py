import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.builtins import *
from reframe.core.backends import getlauncher

@rfm.simple_test
class QECheck(rfm.RunOnlyRegressionTest):
    valid_systems = ['+cpu -login -default']
    version = parameter(['QuantumESPRESSO/7.4-foss-2024a', 'QuantumESPRESSO/7.2-foss-2023a'], type=str)
    valid_prog_environs = ['standard']
    executable = 'pw.x'
    tags = {'calcua', 'performance', 'quantumespresso'}
    num_nodes = parameter([1, 8], type=int)
    #allref =

    @run_before('run')
    def setup_run(self):
        self.num_tasks_per_node = self.current_partition.extras['num_cpus']
        self.num_tasks = self.num_nodes * self.num_tasks_per_node
        self.executable_opts = ['-in', 'ausurf.in', '-nk', str(self.num_nodes), '-pd', '.true.']

    @run_before('run')
    def set_launcher(self):
        self.job.launcher = getlauncher('srun')()

    @sanity_function
    def validate(self):
        return sn.assert_found(r'convergence has been achieved', self.stdout)

    @performance_function('seconds')
    def elapsed_time(self):
        return sn.extractsingle(r'electrons.+\s(?P<time>[0-9.]+)s WALL', self.stdout, 'time', float)

    @run_before('run')
    def set_details(self):
        self.modules = [self.version]
        self.job.options = ['--time 01:00:00', '--switches=1', '--exclusive']

