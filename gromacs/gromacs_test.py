import hpctestlib.sciapps.gromacs.benchmarks
import reframe as rfm
from reframe.core.builtins import *
from reframe.core.backends import getlauncher


@rfm.simple_test
class gromacs_test(hpctestlib.sciapps.gromacs.benchmarks.gromacs_check):
    # build upon existing hpctestlib
    num_nodes = parameter([1, 8])
    version = parameter(['GROMACS/2021.1-intel-2020a.04-UArecipe-CUDA', 'GROMACS/2023.3-foss-2023a-PLUMED-2.9.0'])

    @run_after('init')
    def skip_invalid(self):
        self.skip_if(self.num_nodes == 1 and self.nb_impl == 'cpu', 'cpu tests only multi node')
        self.skip_if(self.num_nodes > 1 and self.nb_impl == 'gpu', 'gpu test only single node')

    @run_after('init')
    def set_test_env(self):
        if self.nb_impl == 'cpu' and  self.version == "GROMACS/2023.3-foss-2023a-PLUMED-2.9.0":
            self.valid_systems = ['+cpu -default -login']
            self.tags = {'gromacs', 'calcua', 'performance'}
            self.modules = [self.version]
            self.valid_prog_environs = ['standard']
        elif self.nb_impl == 'gpu' and self.version == 'GROMACS/2021.1-intel-2020a.04-UArecipe-CUDA':
            self.valid_systems = ['+gpu']
            self.tags = {'gromacs', 'calcua', 'performance', 'gpu'}
            self.modules = [self.version]
            self.valid_prog_environs = ['standard']
        else:
             self.skip(f"skipping {self.version} on {self.nb_impl}")


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
