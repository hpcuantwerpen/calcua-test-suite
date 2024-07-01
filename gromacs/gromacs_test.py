import hpctestlib.sciapps.gromacs.benchmarks
import reframe as rfm
from reframe.core.builtins import *
from reframe.core.backends import getlauncher


@rfm.simple_test
class gromacs_test(hpctestlib.sciapps.gromacs.benchmarks.gromacs_check):
    # build upon existing hpctestlib
    num_nodes = parameter(['1', '6', '8', '10'])

    @run_after('init')
    def skip_invalid(self):
        self.skip_if(self.num_nodes == '1' and self.nb_impl == 'cpu', 'cpu tests only multi node')
        self.skip_if(self.num_nodes > '1' and self.nb_impl == 'gpu', 'gpu test only single node')

    @run_after('init')
    def set_test_env(self):
        if self.nb_impl == 'cpu':
            self.valid_systems = ['*:default-node']
            self.tags = {'gromacs', 'calcua', 'performance'}
            self.modules = ['GROMACS/2021.3-foss-2021a-PLUMED-2.7.2']
            self.valid_prog_environs = ['standard']
        if self.nb_impl == 'gpu':
            self.valid_systems = ['*:nvidia']
            self.tags = {'gromacs', 'calcua', 'performance', 'gpu'}
            self.modules = ['GROMACS/2021.1-intel-2020a.04-UArecipe-CUDA']
            self.valid_prog_environs = ['standard']

    @run_before('run')
    def set_options(self):
        if self.nb_impl == 'cpu':
            if self.current_system.name == 'vaughan':
                self.num_tasks_per_node = 16
            if self.current_system.name in ['leibniz', 'breniac']:
                self.num_tasks_per_node = 7
            self.num_cpus_per_task = 4
            self.num_tasks = int(self.num_nodes) * self.num_tasks_per_node

        if self.nb_impl == 'gpu':
            if self.current_system.name == 'vaughan':
                self.num_devices = 4
                self.num_tasks = 4
                self.num_tasks_per_node = 4
                self.num_cpus_per_task = 6
            if self.current_system.name == 'leibniz':
                self.num_devices = 2
                self.num_tasks = 2
                self.num_tasks_per_node = 2
                self.num_cpus_per_task = 6
            self.extra_resources = {'gpu': {'num_gpus': str(self.num_devices)}}
        
        self.executable_opts += [f'-ntomp {self.num_cpus_per_task}'] # OMP_NUM_THREADS
        self.job.launcher = getlauncher('mpirun')()

    @run_before('run')
    def set_details(self):
        self.job.options = ['--time 01:10:00', '--exclusive']
        if self.nb_impl == 'cpu':
            self.job.options += ['--switches=1']


# @rfm.simple_test
# class gromacs_gpu(hpctestlib.sciapps.gromacs.benchmarks.gromacs_check):
#     # build upon existing hpctestlib
#     valid_systems = ['*:nvidia']
#     tags = {'gromacs', 'calcua', 'performance', 'gpu'}
#     modules = ['GROMACS/2021.1-intel-2020a.04-UArecipe-CUDA']
#     valid_prog_environs = ['standard'] 
#     nb_impl = parameter(['gpu'], loggable=True) # override parent class, cpu only
   
#     @run_before('run')
#     def set_options(self):
#         if self.current_system.name == 'vaughan':
#             self.num_devices = 4
#             self.num_tasks = 4
#             self.num_tasks_per_node = 4
#             self.num_cpus_per_task = 6
#         if self.current_system.name == 'leibniz':
#             self.num_devices = 2
#             self.num_tasks = 2
#             self.num_tasks_per_node = 2
#             self.num_cpus_per_task = 6
#         self.extra_resources = {'gpu': {'num_gpus': str(self.num_devices)}}
#         self.executable_opts += [f'-ntomp {self.num_cpus_per_task}'] # OMP_NUM_THREADS
#         self.job.launcher = getlauncher('mpirun')()

#     @run_before('run')
#     def set_details(self):
#         self.job.options = ['--time 01:10:00', '--exclusive']
