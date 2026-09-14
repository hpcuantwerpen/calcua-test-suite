import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class HelloThreadedExtendedTest(rfm.RegressionTest):
    valid_systems = ["+default", "+login", "+test"]
    valid_prog_environs = ['-mpi']
    sourcepath = 'hworldthread.cpp'
    build_system = 'SingleSource'
    executable_opts = ['16']
    tags = {'calcua', 'basic', 'compilation', 'daily'}
    num_tasks_per_node = 16

    @run_before('compile')
    def set_compilation_flags(self):
        self.build_system.cppflags = ['-DSYNC_MESSAGES']
        self.build_system.cxxflags = ['-std=c++11', '-Wall']
        environ = self.current_environ.name
        self.build_system.cxxflags += ['-pthread']

    @run_before('sanity')
    def set_sanity_patterns(self):
        num_messages = sn.len(sn.findall(r'\[\s?\d+\] Hello, World\!',
                                         self.stdout))
        self.sanity_patterns = sn.assert_eq(num_messages, 16)
