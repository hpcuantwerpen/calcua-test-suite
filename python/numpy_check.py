import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class NumpyTest(rfm.RunOnlyRegressionTest):
    version = parameter(["SciPy-bundle/2024.05-gfbf-2024a", "SciPy-bundle/2021.05-foss-2021a", "Python/3.8.3-intel-2020a"])

    def __init__(self):
        self.descr = 'Test a few typical numpy operations'
        self.valid_prog_environs = ['standard']
        self.time_limit = '20m'

        self.perf_patterns = {
            'dot': sn.extractsingle(
                r'^Dotted two \S* matrices in\s+(?P<dot>\S+)\s+s',
                self.stdout, 'dot', float),
            'svd': sn.extractsingle(
                r'^SVD of a \S* matrix in\s+(?P<svd>\S+)\s+s',
                self.stdout, 'svd', float),
            'cholesky': sn.extractsingle(
                r'^Cholesky decomposition of a \S* matrix in'
                r'\s+(?P<cholesky>\S+)\s+s',
                self.stdout, 'cholesky', float),
            'eigendec': sn.extractsingle(
                r'^Eigendecomposition of a \S* matrix in'
                r'\s+(?P<eigendec>\S+)\s+s',
                self.stdout, 'eigendec', float),
            'inv': sn.extractsingle(
                r'^Inversion of a \S* matrix in\s+(?P<inv>\S+)\s+s',
                self.stdout, 'inv', float),
        }

        self.sanity_patterns = sn.assert_found(r'Numpy version:\s+\S+',
                                               self.stdout)
        self.executable = 'python3'
        self.executable_opts = ['np_ops.py']
        # self.use_multithreading = False
        self.tags = {'apps', 'python', 'numpy', 'performance', 'vsc'}
        self.maintainers = ['Lewih']
        self.valid_systems = ['+default', '+test']

    @run_before('run')
    def setup_run(self):
        self.num_tasks = 1
        self.num_cpus_per_task = 6
        self.env_vars = {
            'OMP_NUM_THREADS': str(self.num_cpus_per_task),
            'MKL_NUM_THREADS': str(self.num_cpus_per_task)
        }

        # parametrized moduel version
        self.modules = [self.version]
        self.job.options = ["--exclusive"]
