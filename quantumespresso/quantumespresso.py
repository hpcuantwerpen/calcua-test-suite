import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.builtins import *
from reframe.core.backends import getlauncher

@rfm.simple_test
class QECheck(rfm.RunOnlyRegressionTest):
    valid_systems = ['*:default-node']
    modules = ['QuantumESPRESSO/7.2-foss-2023a']  
    valid_prog_environs = ['*']  
    executable = 'pw.x'
    tags = {'calcua', 'performance', 'quantumespresso'}
    num_nodes = parameter([1,4,8])
    #allref =  

    @run_after('init')
    def setup_run(self):

        if self.current_system.name == 'vaughan':
            self.num_tasks_per_node = 64
            #nbands = 8
        elif self.current_system.name in ['leibniz', 'breniac']:
            self.num_tasks_per_node = 28
            #nbands = 4
        self.num_tasks = self.num_nodes * self.num_tasks_per_node
        self.executable_opts = ['-in', 'ausurf.in', '-nk', str(self.num_nodes), '-pd', '.true.']
        #self.reference = self.allref[self.num_nodes]

    @run_before('run')
    def set_launcher(self):
        self.job.launcher = getlauncher('srun')()

    @sanity_function
    def validate(self):
        return sn.assert_found(r'convergence has been achieved', self.stdout)

    @performance_function('seconds')
    def elapsed_time(self):
        return sn.extractsingle(r'electrons.+\s(?P<time>\S+)s WALL', self.stdout, 'time', float)

    @run_before('run')
    def set_details(self):
        self.job.options = ['--time 01:00:00', '--switches=1', '--exclusive']

