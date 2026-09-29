import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class HelloMultiLangTest(rfm.RegressionTest):
    lang = parameter(['c', 'cpp'], type=str)
    valid_systems = ["+default", "+login", "+test"]
    valid_prog_environs = ['-mpi']
    tags = {'calcua', 'basic', 'compilation'}

    executable_opts = ['> hello.out']
    sanity_patterns = sn.assert_found(r'Hello, World\!', 'hello.out')

    @run_before('compile')
    def set_sourcepath(self):
        self.sourcepath = f'hworld.{self.lang}'
