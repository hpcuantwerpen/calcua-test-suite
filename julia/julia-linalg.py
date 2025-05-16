import reframe as rfm
import reframe.utility.sanity as sn


class JuliaLinalgBaseTest(rfm.RunOnlyRegressionTest):
    def __init__(self):
        self.valid_prog_environs = ['standard']
        self.sanity_patterns = sn.assert_found(r'Julia version:*',
                                               self.stdout)
        self.modules = ['Julia']
        self.executable = 'julia'
        self.executable_opts = ['linalg.jl']
        self.tags = {'apps', 'julia', '1nodes', 'performance', 'vsc'}
        self.maintainers = ['Lewih']
        self.time_limit = '10m'


@rfm.simple_test
class JuliaLinalgTest(JuliaLinalgBaseTest):
    def __init__(self):
        super().__init__()
        self.descr = 'Test a few typical Julia LinAlg operations'
        self.valid_systems = ['+cpu']
        self.num_tasks_per_node = 1
        self.num_cpus_per_task = 20
        self.tags.add('performance')
        self.executable_opts += [str(self.num_cpus_per_task)]

        self.perf_patterns = {
            'dot': sn.extractsingle(
                r'^Dotted two 4096 x 4096 matrices in\s+(?P<dot>\S+)\s+s',
                self.stdout, 'dot', float),
            'cholesky': sn.extractsingle(
                r'^Cholesky decomposition of a 4096 x 4096 matrix in'
                r'\s+(?P<cholesky>\S+)\s+s',
                self.stdout, 'cholesky', float),
            'lu': sn.extractsingle(
                r'^LU decomposition of a 4096 x 4096 matrix in'
                r'\s+(?P<lu>\S+)\s+s',
                self.stdout, 'lu', float),
        }

    @run_after('setup')
    def set_var_postrun(self):
        self.env_vars = {"JULIA_DEPOT_PATH": "$VSC_SCRATCH/rfm_julia_$SLURM_JOBID"}
        self.postrun_cmds = ['rm -rf $VSC_SCRATCH/rfm_julia_$SLURM_JOBID']

    @run_after('setup')
    def set_options(self):
        self.job.options = ["--exclusive"]

    @run_after('setup')
    def set_num_cpus(self):
        self.sanity_patterns = sn.and_(sn.assert_found(r'BLAS num threads:',
                                                       self.stdout
                                                       ),
                                       self.sanity_patterns) 
                                        