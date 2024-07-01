import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.builtins import *
from reframe.core.backends import getlauncher

@rfm.simple_test
class AbinitCheck(rfm.RunOnlyRegressionTest):
    valid_systems = ['vaughan:default-node', 'leibniz:default-node', 'breniac:default-node']
    modules = ['ABINIT/9.8.2-intel-2020a-hybrid-mkl']  # full name of module unless (D)
    valid_prog_environs = ['*']  # standard, builtin also ok
    executable = 'abinit'
    tags = {'calcua', 'performance', 'abinit'}
    num_nodes = 1
    allref = {1:{'hydrogen':{'vaughan:default-node':{'elapsed_time':(2.1, None, 100, 's')}},
                 'gold':{'vaughan:default-node':{'elapsed_time':(1009.5, None, 100, 's')}}}}     # TODO add ref timings
    test_case = 'gold'

    @run_after('init')
    def setup_run(self):
        self.executable_opts = [f'{self.test_case}.abi']
        if self.current_system.name == 'vaughan':
            self.num_tasks_per_node = 64
        elif self.current_system.name in ['leibniz', 'breniac']:
            self.num_tasks_per_node = 28
        self.num_tasks = self.num_nodes * self.num_tasks_per_node
        self.reference = self.allref[self.num_nodes][self.test_case]

    @run_before('run')
    def set_launcher(self):
        self.job.launcher=getlauncher('srun')()

    @sanity_function
    def validate(self):
        return sn.assert_found(rf'- input  file\s+-> {self.test_case}.abi', f'{self.test_case}.abo')

    @performance_function('seconds')
    def elapsed_time(self):
        return sn.extractsingle(r'Total wall clock time \(s,m,h\):\s+(?P<time>\S+)*', f'{self.test_case}.abo', 'time', float)

    @run_before('run')
    def set_details(self):
        self.job.options = ['--time 01:00:00', '--switches=1', '--exclusive']


