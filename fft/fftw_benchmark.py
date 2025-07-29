# Copyright 2016-2021 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.backends import getlauncher


@rfm.simple_test
class FFTWTest(rfm.RegressionTest):
    valid_systems = ['-gpu -test']
    valid_prog_environs = ['+mpi']
    sourcepath = 'fftw_benchmark.c'
    build_system = 'SingleSource'
    launcher = parameter(['mpirun', 'srun'])

    flags = variable(dict, value={
        'foss-2023a_mpi':   ['-O2', '-lfftw3'],
        'foss-2024a_mpi':   ['-O2', '-lfftw3'],
        'intel-2023a_mpi': ['-O2', '-qmkl'],
        'intel-2024a_mpi': ['-O2', '-qmkl']
    })
    tags = {'calcua', 'performance', 'compilation', 'fftw'}

    def __init__(self):
        self.sanity_patterns = sn.assert_eq(
            sn.count(sn.findall(r'execution time', 'fftw.out')), 1)
        
        self.perf_patterns = {
            'fftw_exec_time': sn.extractsingle(
                r'execution time:\s+(?P<exec_time>\S+)', 'fftw.out',
                'exec_time', float),
        }

    @run_before('run')
    def set_launcher(self):
        self.job.launcher = getlauncher(f'{self.launcher}')()
        # environ = self.current_environ.name
        # if self.current_environ.name == "foss-2024a_mpi":
        #     #self.job.launcher.options = ['--mca prte_keep_fqdn_hostnames 1']
        # debug flags for openmpi
        # self.env_vars['OMPI_MCA_btl_base_verbose']        = '100'
        # self.env_vars['OMPI_MCA_mtl_base_verbose']        = '100'
        # self.env_vars['OMPI_MCA_plm_base_verbose']        = '100'
        # self.env_vars['OMPI_MCA_oob_base_verbose']        = '100'
        # self.env_vars['OMPI_MCA_odls_base_verbose']       = '100'
        # self.env_vars['OMPI_MCA_orte_base_help_aggregate']= '0'
        # self.env_vars['UCX_LOG_LEVEL']                    = 'debug'
        # self.env_vars['OMPI_MCA_pml_ucx_verbose']         = '100'
        # self.env_vars['PMIX_MCA_ptl_base_verbose']        = '10'    
        # self.env_vars['OMPI_MCA_prte_keep_fqdn_hostnames']= '1' 

    @run_before('run')
    def setup_run(self):
        self.num_tasks_per_node = self.current_partition.extras['num_cpus']
        self.num_tasks = 2 * self.current_partition.extras['num_cpus']
        
        self.executable_opts = [f'224 {self.num_tasks} 1000 1 >fftw.out']
        self.prerun_cmds = ['echo "Allocated nodes: $SLURM_NODELIST, tasks: $SLURM_NTASKS, per-node: $SLURM_TASKS_PER_NODE"']

    @run_before('compile')
    def set_compiler_flags(self):
        environ = self.current_environ.name
        self.build_system.cflags = self.flags.get(environ, [])

    @run_before('run')
    def set_details(self):
        self.job.options = ['--time 00:10:00', '--exclusive', '--switches=1']
