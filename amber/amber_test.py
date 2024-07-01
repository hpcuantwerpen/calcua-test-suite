import hpctestlib.sciapps.amber.nve
import reframe as rfm
from reframe.core.builtins import *
from reframe.core.backends import getlauncher


@rfm.simple_test
class amber_test(hpctestlib.sciapps.amber.nve.amber_nve_check):
    # build upon existing hpctestlib
    valid_systems = ['*:default-node']
    tags = {'amber', 'calcua', 'performance', 'cpu'}
    modules = ['Amber/20-intel-2020a-AmberTools-20-patchlevel-6-10']
    valid_prog_environs = ['standard'] 
    num_nodes = parameter(['1', '2', '4', '8'])

    @run_after('init')
    def skip_invalid(self):
        self.skip_if(self.variant != 'mpi', 'skipping cuda variant for the moment')

    @run_before('run')
    def set_options(self):
        # one task per node, many threads
        if self.current_system.name == 'vaughan':
            self.num_tasks = 64 * int(self.num_nodes)
            self.num_tasks_per_node = 64
        if self.current_system.name in ['leibniz', 'breniac']:
            self.num_tasks = 28 * int(self.num_nodes)
            self.num_tasks_per_node = 28
        self.job.launcher = getlauncher('mpirun')()

    @run_before('run')
    def set_details(self):
        self.job.options = ['--time 03:00:00', '--switches=1', '--exclusive']


#TODO fix
# @rfm.simple_test
# class amber_gpu(hpctestlib.sciapps.amber.nve.amber_nve_check):
#     # build upon existing hpctestlib
#     valid_systems = ['*:nvidia']
#     tags = {'amber', 'calcua', 'performance', 'gpu'}
#     modules = ['Amber/22.5-foss-2022a-AmberTools-22.5-CUDA-11.7.0']
#     valid_prog_environs = ['standard'] 
#     variant = parameter(['cuda'], loggable=True) # override parent class, cpu only

#     @run_before('run')
#     def set_options(self):
#         # one task per node, many threads
#         if self.current_system.name == 'vaughan':
#             self.num_tasks = 4
#             self.num_tasks_per_node = 4
#             self.num_devices = 4
#             self.env_vars['CUDA_VISIBLE_DEVICES'] = '0,1,2,3'
#         if self.current_system.name in ['leibniz']:
#             self.num_tasks = 2
#             self.num_nodes = 1
#             self.num_tasks_per_node = 2
#             self.num_devices = 2
#             self.env_vars['CUDA_VISIBLE_DEVICES'] = '0,1'
#         self.job.launcher = getlauncher('mpirun')()
#         self.extra_resources = {'gpu': {'num_gpus': str(self.num_devices)}}

#     @run_before('run')
#     def set_details(self):
#         self.job.options = ['--time 01:10:00', '--switches=1', '--exclusive']
