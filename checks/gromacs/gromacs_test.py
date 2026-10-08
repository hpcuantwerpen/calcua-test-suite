import hpctestlib.sciapps.gromacs.benchmarks
import reframe as rfm
from reframe.core.builtins import *
from reframe.core.backends import getlauncher


@rfm.simple_test
class gromacs_test(hpctestlib.sciapps.gromacs.benchmarks.gromacs_check):
    # build upon existing hpctestlib
    num_nodes = parameter([1, 8], type=int)
    # CUDA builds run in the gpu variant, all other builds in the cpu one, so any
    # build can be tested with -P gromacs_test.version=GROMACS/...
    version = parameter(['GROMACS/2025.3-foss-2025a', 'GROMACS/2023.3-foss-2023a-PLUMED-2.9.0', 'GROMACS/2024.4-foss-2024a-CUDA-12.6.0-PLUMED-2.9.3'], type=str)

    @run_after('init')
    def skip_invalid(self):
        self.skip_if(self.num_nodes == 1 and self.nb_impl == 'cpu', 'cpu tests only multi node')
        self.skip_if(self.num_nodes > 1 and self.nb_impl == 'gpu', 'gpu test only single node')

    @run_after('init')
    def set_test_env(self):
        is_cuda = 'CUDA' in self.version
        self.skip_if(is_cuda != (self.nb_impl == 'gpu'),
                     f"skipping {self.version} on {self.nb_impl}")
        self.modules = [self.version]
        self.valid_prog_environs = ['standard']
        if self.nb_impl == 'gpu':
            self.valid_systems = ['*:nvidia']
            self.tags = {'gromacs', 'calcua', 'performance', 'gpu'}
        else:
            self.valid_systems = ['+cpu -default -login']
            self.tags = {'gromacs', 'calcua', 'performance'}

    @run_before('run')
    def set_options(self):
        if self.nb_impl == 'cpu':
            self.num_cpus_per_task = 4
            num_cpus = self.current_partition.extras['num_cpus']
            self.num_tasks_per_node = num_cpus // self.num_cpus_per_task
            self.num_tasks = int(self.num_nodes) * self.num_tasks_per_node

        if self.nb_impl == 'gpu':
            # only one gpu per test is used
            num_gpus = 1 #self.current_partition.extras['num_gpus'] 
            self.num_tasks = num_gpus
            self.num_cpus_per_task = 6
            self.num_tasks_per_node = self.num_tasks

            self.extra_resources = {'gpu': {'num_gpus': str(num_gpus)}}
        
        self.executable_opts += [f'-ntomp {self.num_cpus_per_task}'] # OMP_NUM_THREADS
        self.job.launcher = getlauncher('mpirun')()

    @run_before('run')
    def set_details(self):
        if self.nb_impl == 'gpu':
            self.job.options = ['--time 01:10:00', '--switches=1'] # no --exclusive, test run in parallel
        else:
            self.job.options = ['--time 01:10:00', '--switches=1', '--exclusive']
