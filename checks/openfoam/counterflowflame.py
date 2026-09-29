# 2D laminar counter-flow methane/air diffusion flame, scaled up from the OpenFOAM.org tutorial
# tutorials/multicomponentFluid/counterFlowFlame2D of OpenFOAM-13.
#
# Why this test exists: the case under src/counterFlowFlame2D carries a constant/thermophysicalTransport
# that the stock tutorial does NOT ship -- the FickianFourier laminar model with per-specie mixture
# diffusion coefficients. That model has caused trouble for a user before, so the sanity check asserts
# the solver actually selected it rather than silently falling back to another transport model.
#
# This is an openfoam.ORG case: it runs through 'foamRun' with the multicomponentFluid solver module
# named in system/controlDict. It will NOT run on the ESI 'OpenFOAM/v2xxx' modules, and not on
# OpenFOAM/10 either, which predates the modular solvers (it used reactingFoam and a different
# case layout). OpenFOAM/11 and /12 ship the same tutorial layout as /13.
#
# Unlike the cavity benchmark next door there is no fixed step count: the time step is Courant
# limited (maxCo 0.4), so a finer mesh also means more steps. Scaling the mesh therefore raises the
# cost faster than the cell count alone suggests.
import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.builtins import *
from reframe.core.backends import getlauncher


@rfm.simple_test
class OpenFOAMCounterFlowFlame2DCheck(rfm.RunOnlyRegressionTest):
    version = parameter(['OpenFOAM/13-foss-2025a'], type=str)
    # class-level so that -S valid_systems/valid_prog_environs=... can override them
    valid_systems = ['vaughan:default', 'leibniz:default', 'breniac:default']
    valid_prog_environs = ['standard']
    sourcesdir = 'src/counterFlowFlame2D'
    executable = 'foamRun'
    executable_opts = ['-parallel', '2>&1', '|', 'tee', 'log.foamRun']
    tags = {'openfoam', 'flame', 'calcua', 'apps', 'performance'}
    maintainers = ['Michele Pugno']

    # Two nodes: 128 ranks on vaughan, 56 on leibniz/breniac -- at least ~50 cores kept busy.
    num_nodes = 2
    # Mesh multiplier on the tutorial's 100 x 40. 5 -> 500 x 200 = 100k cells, i.e. 25x the
    # tutorial, which is a moderate step up rather than a capability run. Override with
    # -S mesh_scale=N. The 5:2 ratio preserves the tutorial's cell aspect ratio.
    mesh_scale = variable(int, value=5)
    # A decomposition thinner than this per rank is not worth measuring.
    min_cells_per_rank = 200

    solver_module = 'multicomponentFluid'
    transport_model = 'FickianFourier'
    end_time = '0.5'

    @property
    def nx(self):
        return 100 * self.mesh_scale

    @property
    def ny(self):
        return 40 * self.mesh_scale

    @property
    def ncells(self):
        return self.nx * self.ny

    @run_after('init')
    def set_descr(self):
        self.descr = (f'OpenFOAM counter-flow flame 2D, {self.nx}x{self.ny} cells, '
                      f'{self.transport_model} transport')
        self.modules = [self.version]

    @run_after('setup')
    def set_num_tasks(self):
        num_cpus = self.current_partition.extras['num_cpus']
        self.num_tasks_per_node = num_cpus
        self.num_tasks = self.num_nodes * num_cpus
        cells_per_rank = self.ncells // self.num_tasks
        self.skip_if(
            cells_per_rank < self.min_cells_per_rank,
            f'{self.ncells} cells over {self.num_tasks} ranks is {cells_per_rank} cells/rank; '
            f'raise mesh_scale (currently {self.mesh_scale}) to keep the ranks busy'
        )

    @run_before('run')
    def set_launcher(self):
        self.job.launcher = getlauncher('srun')()

    @run_before('run')
    def set_prerun(self):
        # blockMesh and decomposePar are serial; only foamRun is measured.
        self.prerun_cmds = [
            'source $FOAM_BASH',
            f'foamDictionary -entry nx -set {self.nx} system/blockMeshDict',
            f'foamDictionary -entry ny -set {self.ny} system/blockMeshDict',
            f'foamDictionary -entry numberOfSubdomains -set {self.num_tasks} '
            'system/decomposeParDict',
            'blockMesh 2>&1 | tee log.blockMesh',
            'decomposePar -force 2>&1 | tee log.decomposePar',
        ]

    @run_before('run')
    def set_details(self):
        # ReFrame's time_limit renders the h:m:s form Slurm accepts; a raw '--time 60m' does not.
        self.time_limit = '1h'
        self.job.options = ['--switches=1', '--exclusive']

    @deferrable
    def check_files(self):
        '''Every stage of the chain produced its log.'''
        return sn.all([sn.path_isfile(f)
                       for f in ('log.blockMesh', 'log.decomposePar', 'log.foamRun')])

    @deferrable
    def assert_mesh(self):
        '''blockMesh honoured the scaled nx/ny and decomposePar finished.'''
        return sn.all([
            sn.assert_found(rf'\s+nCells: {self.ncells}\b', 'log.blockMesh',
                            msg=f'blockMesh did not produce {self.ncells} cells.'),
            sn.assert_found(r'^End', 'log.decomposePar', msg='decomposePar did not finish.'),
        ])

    @deferrable
    def assert_models(self):
        '''The point of the test: FickianFourier was actually selected, on every rank.'''
        nprocs = sn.extractsingle(r'^nProcs\s*:\s*(?P<n>\d+)', 'log.foamRun', 'n', int)
        return sn.all([
            sn.assert_found(rf'^Selecting solver {self.solver_module}', 'log.foamRun',
                            msg=f'solver module {self.solver_module} was not selected.'),
            sn.assert_found(
                rf'^Selecting laminar thermophysical transport model {self.transport_model}',
                'log.foamRun',
                msg=(f'{self.transport_model} was not selected -- constant/thermophysicalTransport '
                     'was ignored or the model fell back to another one.')),
            sn.assert_eq(nprocs, self.num_tasks,
                         msg='foamRun ran on {0} ranks, expected {1}.'),
        ])

    @deferrable
    def assert_completion(self):
        '''The run reached endTime and shut down cleanly.'''
        return sn.all([
            # Not anchored at the end: OpenFOAM 13 prints a unit ('Time = 0.5s').
            sn.assert_found(rf'^Time = {self.end_time}', 'log.foamRun',
                            msg=f'did not reach endTime {self.end_time}.'),
            sn.assert_found(r'^End', 'log.foamRun', msg='foamRun did not reach End.'),
            sn.assert_found(r'^Finalising parallel run', 'log.foamRun',
                            msg='foamRun did not finalise the parallel run.'),
        ])

    @sanity_function
    def validate(self):
        return sn.all([self.check_files(), self.assert_mesh(),
                       self.assert_models(), self.assert_completion()])

    @performance_function('s')
    def execution_time(self):
        '''Solver ExecutionTime at the last time step -- excludes meshing and decomposition.'''
        times = sn.extractall(r'ExecutionTime = (?P<t>\S+) s', 'log.foamRun', 't', float)
        return times[-1]

    @performance_function('steps')
    def timesteps(self):
        '''Step count varies with the mesh (Courant limited), so record it next to the time.'''
        return sn.count(sn.extractall(r'^ExecutionTime = ', 'log.foamRun'))
