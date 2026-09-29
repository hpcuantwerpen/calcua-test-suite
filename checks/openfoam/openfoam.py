# 3D lid-driven cavity (icoFoam) from the OpenFOAM HPC Technical Committee benchmark suite:
# https://develop.openfoam.com/committees/hpc/-/tree/develop/incompressible/icoFoam/cavity3D
# Case data under src/cavity3D is CC BY-SA 4.0, (c) 2022-2024 Wikki GmbH -- see src/cavity3D/COPYING.
# The pipeline below follows the EESSI test-suite implementation of the same benchmark.
#
# The mesh is built by blockMesh at run time, so only the dictionaries live in git. Every mesh size
# runs exactly 15 time steps (endTime/deltaT), which is what makes the wall clock times comparable;
# see the 'Methodology' section of the upstream README.
#
# These are ESI (openfoam.com) cases and use the classic icoFoam solver. The openfoam.org modules on
# CalcUA (OpenFOAM/10 .. OpenFOAM/13) replaced those with 'foamRun -solver ...' and will not run them.
import re

import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.builtins import *
from reframe.core.backends import getlauncher


@rfm.simple_test
class OpenFOAMCavity3DCheck(rfm.RunOnlyRegressionTest):
    mesh = parameter(['1M', '8M', '64M'], type=str)
    version = parameter(['OpenFOAM/v2506-foss-2025a'], type=str)
    # class-level so that -S valid_systems/valid_prog_environs=... can override them
    valid_systems = ['vaughan:default', 'leibniz:default', 'breniac:default']
    valid_prog_environs = ['standard']
    executable = 'icoFoam'
    executable_opts = ['-parallel', '2>&1', '|', 'tee', 'log.icofoam']
    maintainers = ['Michele Pugno']

    # All three cases run this many time steps -- the perf metric divides by it.
    num_timesteps = 15
    # A case is skipped on a partition that cannot reach its rank count within this many nodes.
    max_nodes = 8
    # cores: target rank count. 1M degrades beyond ~128 ranks (too few cells per rank); 64M needs
    # >= 512 ranks to finish in reasonable time, which in practice restricts it to vaughan.
    mesh_params = {
        '1M': {'ncells': 1000000, 'end_time': '0.015', 'cores': 64, 'time_limit': '30m'},
        '8M': {'ncells': 8000000, 'end_time': '0.0075', 'cores': 128, 'time_limit': '1h'},
        '64M': {'ncells': 64000000, 'end_time': '0.00375', 'cores': 512, 'time_limit': '2h'},
    }

    @run_after('init')
    def set_case(self):
        # Stage only the case being run, so it lands in the stage dir root (no cd needed).
        self.sourcesdir = f'src/cavity3D/{self.mesh}/fixedTol'
        self.descr = f'OpenFOAM 3D lid-driven cavity, {self.mesh} cells'
        self.modules = [self.version]
        self.tags = {'openfoam', 'calcua', 'apps', 'performance'}
        if self.mesh == '64M':
            self.tags.add('massive')

    @run_after('setup')
    def set_num_tasks(self):
        cores = self.mesh_params[self.mesh]['cores']
        num_cpus = self.current_partition.extras['num_cpus']
        self.num_nodes = -(-cores // num_cpus)   # ceil
        self.skip_if(
            self.num_nodes > self.max_nodes,
            f'{self.mesh} wants {cores} ranks, which is {self.num_nodes} nodes on '
            f'{self.current_partition.fullname} (limit {self.max_nodes})'
        )
        self.num_tasks_per_node = num_cpus
        self.num_tasks = self.num_nodes * num_cpus

    @run_before('run')
    def set_launcher(self):
        self.job.launcher = getlauncher('srun')()

    @run_before('run')
    def set_prerun(self):
        # A single job does the whole chain; srun inherits the job's rank count. blockMesh is serial.
        self.prerun_cmds = [
            'source $FOAM_BASH',
            f'foamDictionary -entry numberOfSubdomains -set {self.num_tasks} '
            'system/decomposeParDict',
            'blockMesh 2>&1 | tee log.blockMesh',
            'srun redistributePar -decompose -parallel 2>&1 | tee log.decompose',
            'srun renumberMesh -parallel -overwrite 2>&1 | tee log.renumberMesh',
        ]

    @run_before('run')
    def set_details(self):
        # Use ReFrame's time_limit rather than a raw '--time': it renders the h:m:s form that
        # Slurm accepts. A bare '--time 30m' is rejected with 'Invalid --time specification'.
        self.time_limit = self.mesh_params[self.mesh]['time_limit']
        self.job.options = ['--switches=1', '--exclusive']

    @deferrable
    def check_files(self):
        '''Every stage of the chain produced its log.'''
        return sn.all([sn.path_isfile(f) for f in ('log.blockMesh', 'log.decompose',
                                                   'log.renumberMesh', 'log.icofoam')])

    @deferrable
    def assert_completion(self):
        '''The mesh is the expected one, every rank took part, and every stage ran to the end.'''
        ncells = self.mesh_params[self.mesh]['ncells']
        end_time = self.mesh_params[self.mesh]['end_time']
        n_ranks = sn.count(sn.extractall(r'^Processor (?P<rank>[0-9]+)', 'log.decompose', 'rank'))
        return sn.all([
            sn.assert_found(r'^Writing polyMesh with 0 cellZones', 'log.blockMesh',
                            msg='blockMesh failure.'),
            sn.assert_found(rf'\s+nCells: {ncells}\b', 'log.blockMesh',
                            msg=f'blockMesh did not produce {ncells} cells.'),
            sn.assert_eq(n_ranks, self.num_tasks,
                         msg='decomposed into {0} subdomains, expected {1}.'),
            sn.assert_found(r'^Finalising parallel run', 'log.renumberMesh',
                            msg='renumberMesh did not finish.'),
            # Not anchored at the end: some OpenFOAM versions append a unit ('Time = 0.5s').
            # The printed times are exact multiples of deltaT, so no earlier step shares this prefix.
            sn.assert_found(rf'^Time = {re.escape(end_time)}', 'log.icofoam',
                            msg=f'icoFoam did not reach the last time step ({end_time}).'),
            sn.assert_found(r'^Finalising parallel run', 'log.icofoam',
                            msg='icoFoam did not finish.'),
        ])

    @deferrable
    def assert_convergence(self):
        '''Continuity must not drift -- catches a silently wrong pressure solve.'''
        cont_err = sn.extractall(r'cumulative = (?P<cont>\S+)', 'log.icofoam', 'cont', float)
        return sn.assert_le(sn.abs(cont_err[-1]), 1e-15,
                            msg='cumulative continuity error {0} > {1}; check the pressure solver.')

    @sanity_function
    def validate(self):
        return sn.all([self.check_files(), self.assert_completion(), self.assert_convergence()])

    @performance_function('s/timestep')
    def time_per_timestep(self):
        clock = sn.extractall(r'ClockTime = (?P<t>\S+)', 'log.icofoam', 't', float)
        return clock[-1] / self.num_timesteps
