import hpctestlib.sciapps.amber.nve
import reframe as rfm
from reframe.core.builtins import *
from reframe.core.backends import getlauncher


@rfm.simple_test
class amber_test(hpctestlib.sciapps.amber.nve.amber_nve_check):
    # build upon existing hpctestlib
    valid_systems = ['+default', '+test -login']
    tags = {'amber', 'calcua', 'performance', 'cpu'}
    version = parameter(['Amber/24.3-foss-2023a-AmberTools-24.10'])
    valid_prog_environs = ['standard'] 
    num_nodes = parameter([2, 8])
    
    @run_after('init')
    def skip_invalid(self):
        self.skip_if(self.variant != 'mpi', 'skipping cuda variant for the moment')

    @run_before('run')
    def set_options(self):
        self.num_tasks_per_node = self.current_partition.extras['num_cpus']
        self.num_tasks = int(self.num_nodes) * self.num_tasks_per_node
        self.job.launcher = getlauncher('mpirun')()

    @run_before('run')
    def set_details(self):
        self.modules = [self.version]
        self.job.options = ['--time 01:00:00', '--switches=1', '--exclusive']


@rfm.simple_test
class amber_gpu(hpctestlib.sciapps.amber.nve.amber_nve_check):
    # build upon existing hpctestlib
    valid_systems = ['*:nvidia']
    tags = {'amber', 'calcua', 'performance', 'gpu'}
    version = parameter(['Amber/24.3-foss-2023a-AmberTools-24.10-CUDA-12.1.1'])
    valid_prog_environs = ['standard'] 
    variant = parameter(['cuda'], loggable=True) # override parent class, gpu only

    @run_before('run')
    def set_options(self):
        # one task per node, many threads
        if self.current_system.name == 'vaughan':
            self.num_tasks = 1
            self.num_tasks_per_node = 1
            self.num_devices = 1
            # self.env_vars['CUDA_VISIBLE_DEVICES'] = '0,1,2,3'
        if self.current_system.name in ['leibniz']:
            self.num_tasks = 1
            self.num_nodes = 1
            self.num_tasks_per_node = 1
            self.num_devices = 1
            # self.env_vars['CUDA_VISIBLE_DEVICES'] = '0,1'
        self.job.launcher = getlauncher('mpirun')()
        self.extra_resources = {'gpu': {'num_gpus': str(self.num_devices)}}

    @run_before('run')
    def set_details(self):
        self.modules = [self.version]
        self.job.options = ['--time 01:10:00', '--switches=1']
