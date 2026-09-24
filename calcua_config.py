import os

# Where reframe writes output/stage/performance/reports: the shared directory unless
# CALCUA_LOGDIR is set (e.g. to $VSC_DATA/reframe/logs). run_calcua.sh and push_to_mongo.py read the same variable.
logdir = os.environ.get('CALCUA_LOGDIR', '/apps/antwerpen/reframe/logs').rstrip('/')
cluster = os.environ.get('VSC_INSTITUTE_CLUSTER', 'unknown')
# The checks of this checkout, wherever it lives.
checkpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'checks')

standard_mode_options = [
    '--exec-policy=async',
    f'--output={logdir}/output/',
    f'--perflogdir={logdir}/performance/',
    f'--stage={logdir}/stage/',
    f'--report-file={logdir}/reports/last-{cluster}.json',
    '--nocolor',
    f'--checkpath={checkpath}/'
]


print("Loading Calcua config file")

# use 'info' to log to syslog
syslog_level = 'warning'

# To run jobs on the calcua cluster, you need to be a member of the following
# vsc group
calcua_account_string_tier2 = '-A ap_calcua_staff'

# List of programming environments used in the cpu partitions
cpu_env_list = ['standard', 'foss-2023a', 'foss-2024a', 'intel-2023a',
                'foss-2023a_mpi', 'foss-2024a_mpi', 'intel-2023a_mpi', 'intel-2024a', 'intel-2024a_mpi', 'foss-2025a', 'intel-2025a', 'foss-2025a_mpi', 'intel-2025a_mpi']

# Site Configuration
site_configuration = {
    'modes':
    [
        {
            'name': 'daily',
            # change exec-policy to serial
            'options': standard_mode_options[1:len(standard_mode_options)] + ['--flex-alloc-nodes="1"', '--exec-policy=async', '-t daily']
        },
        {
            'name': 'calcua',
            'options': standard_mode_options + ['-T massive', '-T daily'],
        },
        {
            'name': 'all',
            'options': standard_mode_options
        }
    ],
    'systems': [
        {
            'name': 'vaughan',
            'descr': 'VSC Tier-2 Vaughan',
            'hostnames': ['.*vaughan'],
            'modules_system': 'lmod',
            'partitions': [
                {
                    'name': 'login',
                    'scheduler': 'local',
                    'modules': [],
                    'access': [],
                    'environs': ['standard'],
                    'extras': {'num_cpus': 32},
                    'features': ['cpu', 'login'],
                    'descr': 'tests in the local node (no job)',
                    'max_jobs': 18,
                    'launcher': 'local',
                },
                {
                    'name': 'default',
                    'scheduler': 'slurm',
                    'modules': [],
                    'access': [calcua_account_string_tier2],
                    'environs': cpu_env_list,
                    'extras': {'num_cpus': 64},
                    'features': ['cpu', 'default'],
                    'descr': 'default-node jobs',
                    'max_jobs': 18,
                    'launcher': 'local',
                },
                {
                    'name': 'zen2',
                    'scheduler': 'slurm',
                    'modules': [],
                    'access': [calcua_account_string_tier2, '-p zen2'],
                    'environs': cpu_env_list,
                    'features': ['cpu'],
                    'extras': {'num_cpus': 64},
                    'descr': 'default-node jobs',
                    'max_jobs': 18,
                    'launcher': 'local',
                },
                {
                    'name': 'zen3',
                    'scheduler': 'slurm',
                    'modules': [],
                    'access': [calcua_account_string_tier2, '-p zen3'],
                    'environs': cpu_env_list,
                    'features': ['cpu'],
                    'extras': {'num_cpus': 64},
                    'descr': 'default-node jobs',
                    'max_jobs': 18,
                    'launcher': 'local',
                },
                {
                    'name': 'zen3_512',
                    'scheduler': 'slurm',
                    'modules': [],
                    'access': [calcua_account_string_tier2, '-p zen3_512'],
                    'environs': cpu_env_list,
                    'features': ['cpu'],
                    'extras': {'num_cpus': 64},
                    'descr': 'default-node jobs',
                    'max_jobs': 18,
                    'launcher': 'local',
                },
                # {
                #     'name': 'rocky9_test',
                #     'scheduler': 'slurm',
                #     'modules': [],
                #     'access': [calcua_account_string_tier2, '--reservation=rocky9'],
                #     'environs': cpu_env_list,
                #     'features': ['cpu', 'test'],
                #     'extras': {'num_cpus': 64},
                #     'descr': 'jobs with rocky9 reservation',
                #     'max_jobs': 18,
                #     'launcher': 'local',
                # },
                {
                    'name': 'nvidia',
                    'scheduler': 'slurm',
                    'access': [calcua_account_string_tier2, '-p ampere_gpu'],
                    'environs': ['CUDA', 'standard'],
                    'descr': 'Nvidia ampere node',
                    'max_jobs': 18,
                    'launcher': 'local',
                    'resources': [
                        {
                            'name': 'gpu',
                            'options': ['--gpus-per-node={num_gpus}'],
                        },
                    ],
                    'extras': {'num_cpus': 64, 'num_gpus': 4},
                    'features': ['gpu', 'nvidia'],

                },
                {
                    'name': 'amd',
                    'scheduler': 'slurm',
                    'access': [calcua_account_string_tier2, '-p arcturus_gpu'],
                    'environs': ['standard'],
                    'descr': 'AMD GPU node',
                    'max_jobs': 18,                #     'launcher': 'local',
                    'launcher': 'local',
                    'resources': [
                        {
                        'name': 'gpu',
                        'options': ['--gpus-per-node={num_gpus}'],
                        },
                    ],
                    'extras': {'num_cpus': 64, 'num_gpus': 2},
                    'features': ['gpu', 'amd'],
                }
            ]
        },
        {
            'name': 'leibniz',
            'descr': 'VSC Tier-2 Leibniz',
            'hostnames': ['.*leibniz'],
            'modules_system': 'lmod',
            'partitions': [
                {
                    'name': 'login',
                    'scheduler': 'local',
                    'modules': [],
                    'access': [],
                    'environs': ['standard'],
                    'extras': {'num_cpus': 56},
                    'features': ['cpu', 'login'],
                    'descr': 'tests in the local node (no job)',
                    'max_jobs': 18,
                    'launcher': 'local',
                },
                {
                    'name': 'default',
                    'scheduler': 'slurm',
                    'modules': [],
                    'access': [calcua_account_string_tier2],
                    'environs': cpu_env_list,
                    'extras': {'num_cpus': 28},
                    'features': ['cpu', 'default'],
                    'descr': 'default-node jobs',
                    'max_jobs': 18,
                    'launcher': 'local',
                },
                {
                    'name': 'broadwell',
                    'scheduler': 'slurm',
                    'modules': [],
                    'access': [calcua_account_string_tier2, '-p broadwell'],
                    'environs': cpu_env_list,
                    'extras': {'num_cpus': 28},
                    'features': ['cpu'],
                    'descr': 'broadwell-node jobs',
                    'max_jobs': 18,
                    'launcher': 'local',
                },
                {
                    'name': 'broadwell_256',
                    'scheduler': 'slurm',
                    'modules': [],
                    'access': [calcua_account_string_tier2, '-p broadwell_256'],
                    'environs': cpu_env_list,
                    'extras': {'num_cpus': 28},
                    'features': ['cpu'],
                    'descr': 'broadwell_256-node jobs',
                    'max_jobs': 18,
                    'launcher': 'local',
                },
                {
                    'name': 'nvidia',
                    'scheduler': 'slurm',
                    'access': [calcua_account_string_tier2, '-p pascal_gpu'],
                    'environs': ['CUDA', 'standard'],
                    'descr': 'Nvidia pascal nodes',
                    'max_jobs': 18,
                    'launcher': 'local',
                    'resources': [
                        {
                            'name': 'gpu',
                            'options': ['--gpus-per-node={num_gpus}'],
                        },
                    ],
                    'extras': {'num_cpus': 28, 'num_gpus': 2},
                    'features': ['gpu', 'nvidia', 'deprecated'],
                }
            ]
        },
        {
            'name': 'breniac',
            'descr': 'VSC Tier-2 Breniac',
            'hostnames': ['.*breniac'],
            'modules_system': 'lmod',
            'partitions': [
                {
                    'name': 'login',
                    'scheduler': 'local',
                    'modules': [],
                    'access': [],
                    'environs': ['standard'],
                    'extras': {'num_cpus': 28},
                    'features': ['cpu', 'login'],
                    'descr': 'tests in the local node (no job)',
                    'max_jobs': 18,
                    'launcher': 'local',
                },
                {
                    'name': 'default',
                    'scheduler': 'slurm',
                    'modules': [],
                    'access': [calcua_account_string_tier2],
                    'environs': cpu_env_list,
                    'extras': {'num_cpus': 28},
                    'features': ['cpu', 'default'],
                    'descr': 'default-node jobs',
                    'max_jobs': 18,
                    'launcher': 'local',
                },
                {
                    'name': 'skylake',
                    'scheduler': 'slurm',
                    'modules': [],
                    'access': [calcua_account_string_tier2, '-p skylake'],
                    'environs': cpu_env_list,
                    'extras': {'num_cpus': 28},
                    'features': ['cpu'],
                    'descr': 'skylake-node jobs',
                    'max_jobs': 18,
                    'launcher': 'local',
                },
            ]
        },
    ],
    'environments': [
        {
            'name': 'standard', 'cc': 'gcc', 'cxx': 'g++', 'ftn': 'gfortran', 'features': ['default']},
        {
            'name': 'foss-2023a', 'cc': 'gcc', 'cxx': 'g++', 'ftn': 'gfortran', 'modules': ['foss/2023a']},
        {
            'name': 'foss-2023a_mpi', 'cc': 'mpicc', 'cxx': 'mpicxx', 'ftn': 'mpifort', 'modules': ['foss/2023a'], 'features': ['mpi', 'fftw']},
        {
            'name': 'foss-2024a', 'cc': 'gcc', 'cxx': 'g++', 'ftn': 'gfortran', 'modules': ['foss/2024a']},
        {
            'name': 'foss-2024a_mpi', 'cc': 'mpicc', 'cxx': 'mpicxx', 'ftn': 'mpifort', 'modules': ['foss/2024a'], 'features': ['mpi', 'fftw']},
{
            'name': 'foss-2025a', 'cc': 'gcc', 'cxx': 'g++', 'ftn': 'gfortran', 'modules': ['foss/2025a']},
        {
            'name': 'foss-2025a_mpi', 'cc': 'mpicc', 'cxx': 'mpicxx', 'ftn': 'mpifort', 'modules': ['foss/2025a'], 'features': ['mpi']},
        {
            'name': 'intel-2023a', 'cc': 'icx', 'cxx': 'icpx', 'ftn': 'ifx', 'modules': ['intel/2023a']},
        {
            'name': 'intel-2023a_mpi', 'cc': 'mpiicc', 'cxx': 'mpiicpc', 'ftn': 'mpiifort', 'modules': ['intel/2023a'], 'features': ['mpi', 'fftw']},
        {
            'name': 'intel-2024a', 'cc': 'icx', 'cxx': 'icpx', 'ftn': 'ifx', 'modules': ['intel/2024a']},
        {
            'name': 'intel-2024a_mpi', 'cc': 'mpiicx', 'cxx': 'mpiicpx', 'ftn': 'mpiifx', 'modules': ['intel/2024a'], 'features': ['mpi', 'fftw']},
 {
            'name': 'intel-2025a', 'cc': 'icx', 'cxx': 'icpx', 'ftn': 'ifx', 'modules': ['intel/2025a']},
        {
            'name': 'intel-2025a_mpi', 'cc': 'mpiicx', 'cxx': 'mpiicpx', 'ftn': 'mpiifx', 'modules': ['intel/2025a'], 'features': ['mpi']},
        {
            'name': 'CUDA',
            'modules': ['CUDA/12.8.0'],
            'cc': 'nvcc',
            'cxx': 'nvcc',
            'features': ['cuda'],
        },
    ],
    'general': [
        {
            'purge_environment': False,
            # avoid loading the module before submitting the job
            'resolve_module_conflicts': False,
        }
    ],
    'logging': [
        {
            'level': 'debug',
            'handlers': [
                {
                    'type': 'stream',
                    'name': 'stdout',
                    'level': 'info',
                    'format': '%(message)s',
                },
            ],
        }
    ],
}
