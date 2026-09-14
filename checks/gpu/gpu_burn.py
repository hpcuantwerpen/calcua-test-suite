import os
import reframe as rfm
import reframe.utility.sanity as sn

@rfm.simple_test
class GPU_Burn_nvidia(rfm.RunOnlyRegressionTest):
    descr = "GPU burn test on nvidia node"
    valid_systems = ["+nvidia"]
    valid_prog_environs = ["CUDA"]
    modules = ['git']
    env_vars = {'CUDAPATH': '$EBROOTCUDA'}
    time_limit = '10m'
    prerun_cmds = ['git clone https://github.com/wilicc/gpu-burn.git', 'cd gpu-burn']
    executable = '--output=rfm_GPUBURN_nvidia_node-%N.out ./gpu_burn 20'
    tags = {"gpu", "burn", "performance", "vsc"}
    num_devices = 0
    num_tasks_per_node = 1

    @run_before('run')
    def set_options(self):
        if self.current_system.name == 'vaughan':
            # works on 4 gpus
            self.num_devices = 4
            self.num_tasks = 1
            self.num_cpus_per_task = 64
            self.prerun_cmds += ['make']
        if self.current_system.name == 'leibniz':
            # works on 2 nodes
            self.num_devices = 2
            self.num_tasks = 2
            self.num_cpus_per_task = 28
            self.prerun_cmds += ['COMPUTE=60 make']
        
        self.extra_resources = {'gpu': {'num_gpus': str(self.num_devices)}}
        self.descr = f'Nvidia gpu burn test on {self.current_system.name} with {self.num_devices} gpus'

    @sanity_function
    def assert_job(self):
        result = True
        for n in sorted(self.job.nodelist):
            node = n.split('.')[0]
            result = sn.and_(sn.and_(sn.assert_found(r'OK', self.stagedir+f'/gpu-burn/rfm_GPUBURN_nvidia_node-{node}.out'), sn.assert_not_found(r'FAULTY',  self.stagedir+f'/gpu-burn/rfm_GPUBURN_nvidia_node-{node}.out')), result)
        return result

    @performance_function('Gflop/s')
    def get_gflops(self, device=0, node=None):
        # take starting from item -1 (last match) 
        return sn.extractsingle(r'\((?P<gflops>\S+) Gflop/s\)',  self.stagedir+f'/gpu-burn/rfm_GPUBURN_nvidia_node-{node}.out', 'gflops', float, item=(-device-1))

    @run_before('performance')
    def set_perf_variables(self):
        '''Build the dictionary with all the performance variables.'''
        self.perf_variables = {}
        # for dry runs, check if nodelist is empty
        if self.job.nodelist:
            for n in self.job.nodelist:
                node =n.split('.')[0]
                device = 0
                for x in range(self.num_devices):
                    self.perf_variables[f'{node}_device{self.num_devices-device-1}'] = self.get_gflops(device=self.num_devices-device, node=node)
                    device += 1
