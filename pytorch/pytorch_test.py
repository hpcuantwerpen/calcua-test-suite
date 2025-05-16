import reframe as rfm
from reframe.core.builtins import *
import hpctestlib.ml.pytorch.horovod


@rfm.simple_test
class pytorch_cuda(hpctestlib.ml.pytorch.horovod.pytorch_cnn_check):
    # build upon existing hpctestlib
    valid_systems = ['*:nvidia']
    tags = {'pytorch',  'torch', 'nvidia', 'gpu', 'calcua', 'performance'}
    # bundle contains torchvision
    version = parameter([['PyTorch-bundle/1.13.1-foss-2022a-CUDA-11.7.0 ', 'Horovod/0.28.1-foss-2022a-CUDA-11.7.0-PyTorch-1.13.1'], ])
    valid_prog_environs = ['standard'] 
    num_iters = 40

    @run_before('run')
    def set_options(self):
        self.modules = [self.version]
        if self.current_system.name == 'vaughan':
            # works on 4 gpus
            self.num_devices = 4
            self.num_tasks = 4
            self.num_cpus_per_task = 16
        if self.current_system.name == 'leibniz':
            # works on 2 nodes
            self.num_devices = 2
            self.num_tasks = 2
            self.num_cpus_per_task = 14

        self.extra_resources = {'gpu': {'num_gpus': str(self.num_devices)}}
