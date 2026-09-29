import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.backends import getlauncher

all_files = {
    'kfd': {'mount': '/dev/kfd', 'mode': 666, 'system': 'vaughan:amd', 'extras': '{"gpu": {"num_gpus": str(2)}}'}
}


@rfm.simple_test
class CalcuaExistTest(rfm.RunOnlyRegressionTest):
    descr = "test file exists "
    fs = parameter(all_files.keys(), type=str)
    valid_prog_environs = ["standard"]
    maintainers = ['lewih']
    time_limit = '1m'
    num_tasks = -1
    num_tasks_per_node = 1
    tags = {"calcua", "fs"}

    @run_after('init')
    def set_param(self):
        self.valid_systems = [all_files[self.fs]['system']]
        path = all_files[self.fs]['mount']
        self.descr += path
        exe = """python3 -c 'import os;print(os.uname().nodename, os.path.exists(os.path.realpath("{}")))'"""
        self.executable = exe.format(path)
        self.extra_resources = eval(all_files[self.fs]['extras'])
    
    @run_after("setup")
    def set_launcher(self):
        if self.current_partition.name == "login":
            self.job.launcher = getlauncher('local')()
        else:
            self.job.launcher.options = ['--overlap']
            self.job.launcher = getlauncher('srun')()

    @sanity_function
    def assert_test_1(self):
        return sn.and_(sn.assert_found(r'True$', self.stdout), sn.assert_not_found(r'False$', self.stdout))


@rfm.simple_test
class CalcuaModeTest(rfm.RunOnlyRegressionTest):
    descr = "test file permissions "
    fs = parameter(all_files.keys(), type=str)
    valid_prog_environs = ["standard"]
    maintainers = ['lewih']
    time_limit = '1m'
    num_tasks = -1
    num_tasks_per_node = 1
    tags = {"calcua", "fs"}

    @run_after('init')
    def set_param(self):
        variant = CalcuaExistTest.get_variant_nums(fs=lambda x: x==self.fs)
        self.depends_on(CalcuaExistTest.variant_name(variant[0]))

        self.valid_systems = [all_files[self.fs]['system']]
        path = all_files[self.fs]['mount']
        mode = all_files[self.fs]['mode']
        self.descr += path
        exe = """ python3 -c 'import os;print(oct(os.stat(os.path.realpath("{}")).st_mode)[-3:] == "{}")'"""
        self.executable = exe.format(path, mode)
        self.extra_resources = eval(all_files[self.fs]['extras'])

    @run_after("setup")
    def set_launcher(self):
        if self.current_partition.name != "login":
            self.job.launcher = getlauncher('srun')()
            self.job.launcher.options = ['--overlap']

    @sanity_function
    def assert_test(self):
        return sn.and_(sn.assert_found(r'True$', self.stdout), sn.assert_not_found(r'False$', self.stdout))
