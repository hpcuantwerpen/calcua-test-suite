import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.builtins import *
from reframe.core.backends import getlauncher


@rfm.simple_test
class GaussianCheck(rfm.RunOnlyRegressionTest):
    version = parameter(['Gaussian/g16_c01-avx2'], type=str)
    valid_systems = ['vaughan:default']
    valid_prog_environs = ['standard']
    executable = 'g16'
    tags = {'calcua', 'performance', 'gaussian'}
    output_file = 'g16-test.log'

    @run_before('run')
    def setup_run(self):
        self.executable_opts = [f'< g16-test.com > {self.output_file}']
        self.num_cpus_per_task = self.current_partition.extras['num_cpus']
        self.num_tasks = 1
        self.num_tasks_per_node = 1
        self.job.launcher=getlauncher('srun')()

    @sanity_function
    def validate(self):
        return sn.assert_found(r'Normal termination of Gaussian.*', self.output_file)

    @performance_function('seconds')
    def elapsed_time(self):
        # one 'Elapsed time' line per Gaussian step (opt, then freq): add them up
        steps = sn.evaluate(sn.extractall(
            r'Elapsed time:\s+(?P<d>\d+)\s+days\s+(?P<h>\d+)\s+hours\s+(?P<m>\d+)\s+minutes\s+(?P<s>\S+)\s+seconds',
            self.output_file, ('d', 'h', 'm', 's'), (int, int, int, float)))
        return sum(d*24*60*60 + h*60*60 + m*60 + s for d, h, m, s in steps)

    @run_before('run')
    def set_details(self):
        self.modules = [self.version]
        self.job.options = ['--time 01:00:00', '--switches=1']

