import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.backends import getlauncher


class NamdBaseTest(rfm.RunOnlyRegressionTest):
    num_nodes = parameter([1, 2, 4, ])

    def __init__(self, arch):
        self.descr = f'NAMD check on {arch}, number of nodes: {self.num_nodes}, apoa1 and stmv(4 nodes only)'
        # fallback module load
        self.modules = ['NAMD']

        self.sanity_patterns = sn.assert_found(r'WRITING EXTENDED SYSTEM TO OUTPUT FILE AT STEP',
                                               self.stdout)
        self.perf_patterns = {
            'days_ns': sn.avg(sn.extractall(
                r'Info: Benchmark time: \S+ CPUs \S+ '
                r's/step (?P<days_ns>\S+) days/ns \S+ MB memory',
                self.stdout, 'days_ns', float))
        }

        self.maintainers = ['Lewih']

        self.tags = {'apps', 'namd', 'performance', 'vsc'}
        self.tags.add(f'{self.num_nodes}nodes')

    def download_material(self):
        if int(self.num_nodes) in {1, 2}:
            self.prerun_cmds = [
                'wget https://www.ks.uiuc.edu/Research/namd/utilities/apoa1.zip', 'unzip apoa1.zip']
            return "apoa1"
        if int(self.num_nodes) > 2:
            self.prerun_cmds = [
                'wget https://www.ks.uiuc.edu/Research/namd/utilities/stmv.zip', 'unzip stmv.zip']
            return "stmv"

    def create_nodelist(self):
        # scheduler commands
        # slurm prerun commands
        self.prerun_cmds += ['echo Number of nodes: $SLURM_NPROCS',
                             'for node in `scontrol show hostnames`; do echo host $node >>mynodes; done']


@rfm.simple_test
class Namd_SMP_CPUTest(NamdBaseTest):
    # NAMD SMP CPU test
    version = parameter(['NAMD/2.14-verbs-smp'])

    def __init__(self):
        self.tags.add('smp')
        self.time_limit = '20m'

        self.valid_systems = ['+default']
        self.valid_prog_environs = ['standard']
        super().__init__('cpu')

    @run_before('run')
    def setup_run(self):
        self.num_cpus_per_task = self.current_partition.extras['num_cpus']
        self.num_tasks = int(self.num_nodes)
        configFile = self.download_material()

        self.modules = [self.version]

        self.create_nodelist()

        self.executable = f'charmrun ++p {self.num_cpus_per_task*self.num_tasks} ++ppn {self.num_cpus_per_task} ++nodelist mynodes $EBROOTNAMD/namd2 {configFile}/{configFile}.namd'


@rfm.simple_test
class Namd_NotSMP_CPUTest(NamdBaseTest):
    # NAMD notSMP CPU test
    version = parameter(['NAMD/2.14-verbs'])

    def __init__(self):
        self.time_limit = '20m'

        self.valid_systems = ['+default']

        self.valid_prog_environs = ['standard']
        super().__init__('cpu')

    @run_before('run')
    def setup_run(self):
        self.num_cpus_per_task = self.current_partition.extras['num_cpus']
        self.num_tasks = int(self.num_nodes)

        configFile = self.download_material()

        self.modules = [self.version]

        # select launcher
        self.create_nodelist()
        self.executable = f'charmrun ++p {self.num_cpus_per_task*self.num_tasks} ++nodelist mynodes $EBROOTNAMD/namd2 {configFile}/{configFile}.namd'