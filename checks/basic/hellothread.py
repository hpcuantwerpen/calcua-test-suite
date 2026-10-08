import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class HelloThreadedExtendedTest(rfm.RegressionTest):
    valid_systems = ["+default", "+login"]
    valid_prog_environs = ['-mpi']
    sourcepath = 'hworldthread.cpp'
    build_system = 'SingleSource'
    executable_opts = ['16']
    tags = {'calcua', 'basic', 'compilation'}
    num_cpus_per_task = 16   # one process running 16 threads

    @run_before('compile')
    def set_compilation_flags(self):
        self.build_system.cppflags = ['-DSYNC_MESSAGES']
        self.build_system.cxxflags = ['-std=c++11', '-Wall']
        self.build_system.cxxflags += ['-pthread']

    @run_before('sanity')
    def set_sanity_patterns(self):
        num_messages = sn.len(sn.findall(r'\[\s?\d+\] Hello, World\!',
                                         self.stdout))
        self.sanity_patterns = sn.assert_eq(num_messages, 16)
