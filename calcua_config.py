from py import builtin
import os
import grp
standard_mode_options = [
    '--exec-policy=async',
    '--output=/apps/antwerpen/reframe/logs/output/',
    '--perflogdir=/apps/antwerpen/reframe/logs/performance/',
    '--stage=/apps/antwerpen/reframe/logs/stage/',
    '--report-file=/apps/antwerpen/reframe/logs/reports/last-$VSC_INSTITUTE_CLUSTER.json',
    '--nocolor',
    '--checkpath=/apps/antwerpen/reframe/testsuite/calcua-test-suite/'
]


print("Loading Calcua config file")

# use 'info' to log to syslog
syslog_level = 'warning'

# To run jobs on the calcua cluster, you need to be a member of the following
# vsc group
calcua_account_string_tier2 = '-A ap_calcua_staff'

# List of programming environments used in the cpu partitions
cpu_env_list = ['standard', 'foss-2023a', 'intel-2023a',
                'foss-2023a_mpi', 'intel-2023a_mpi', 'intel-2024a', 'intel-2024a_mpi']

# Site Configuration
site_configuration = {
    'modes':
    [
        {
            'name': 'basic',
            'options': standard_mode_options + ['--tag=basic'],
        },
        {
            'name': 'vsc',
            'options': standard_mode_options + ['--tag=vsc'],
        },
        {
            'name': 'calcua',
            'options': standard_mode_options + ['--tag=calcua'],
        },
        {
            'name': 'numpy',
            'options': standard_mode_options + ['--tag=python'],
        },
        {
            'name': 'nogpu',
            'options': standard_mode_options + ['--exclude-tag=gpu'],
        },
        {
            'name': 'gpu',
            'options': standard_mode_options + ['--tag=gpu'],
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
                {
                    'name': 'rocky9_test',
                    'scheduler': 'slurm',
                    'modules': [],
                    'access': [calcua_account_string_tier2, '--reservation=rocky9'],
                    'environs': cpu_env_list,
                    'features': ['cpu', 'test'],
                    'extras': {'num_cpus': 64},
                    'descr': 'jobs with rocky9 reservation',
                    'max_jobs': 18,
                    'launcher': 'local',
                },
                {
                    'name': 'nvidia',
                    'scheduler': 'slurm',
                    'access': [calcua_account_string_tier2, '-p ampere_gpu'],
                    'environs': ['CUDA', 'standard'],
                    'descr': 'Nvidia ampere node',
                    'max_jobs': 18,
                    'launcher': 'srun',
                    'resources': [
                        {
                            'name': 'gpu',
                            'options': ['--gpus-per-node={num_gpus}'],
                        },
                    ],
                    'extras': {'num_cpus': 64, 'num_gpus': 4},
                    'features': ['gpu'],

                },
                # {
                #     'name': 'amd',
                #     'scheduler': 'slurm',
                #     'access': [calcua_account_string_tier2, '-p arcturus_gpu'],
                #     'environs': ['standard'],
                #     'descr': 'AMD GPU node',
                #     'max_jobs': 18,                #     'launcher': 'srun',
                #     'resources': [
                #         {
                #         'name': 'gpu',
                #         'options': ['--gpus-per-node={num_gpus}'],
                #         },
                #     ]
                # }
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
                    'name': 'rocky9_test',
                    'scheduler': 'slurm',
                    'modules': [],
                    'access': [calcua_account_string_tier2, '--reservation=rocky9'],
                    'environs': cpu_env_list,
                    'extras': {'num_cpus': 28},
                    'features': ['cpu', 'test'],
                    'descr': 'jobs with rocky9 reservation',
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
                    'launcher': 'srun',
                    'resources': [
                        {
                            'name': 'gpu',
                            'options': ['--gpus-per-node={num_gpus}'],
                        },
                    ],
                    'extras': {'num_cpus': 28, 'num_gpus': 2},
                    'features': ['gpu'],
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
            'name': 'foss-2023a_mpi', 'cc': 'mpicc', 'cxx': 'mpicxx', 'ftn': 'mpifort', 'modules': ['foss/2023a'], 'features': ['mpi']},
        {
            'name': 'intel-2023a', 'cc': 'icx', 'cxx': 'icpx', 'ftn': 'ifx', 'modules': ['intel/2023a']},
        {
            'name': 'intel-2023a_mpi', 'cc': 'mpiicc', 'cxx': 'mpiicpc', 'ftn': 'mpiifort', 'modules': ['intel/2023a'], 'features': ['mpi']},
        {
            'name': 'intel-2024a', 'cc': 'icx', 'cxx': 'icpx', 'ftn': 'ifx', 'modules': ['intel/2024a']},
        {
            'name': 'intel-2024a_mpi', 'cc': 'mpiicx', 'cxx': 'mpiicpx', 'ftn': 'mpiifx', 'modules': ['intel/2024a'], 'features': ['mpi']},

        # {
        #     'name': 'foss-2021a', 'cc': 'mpicc', 'cxx': 'mpicxx',
        #     'ftn': 'mpif90', 'modules': ['foss/2021a'],},
        # {
        #     'name': 'intel-2021a',
        #     'modules': ['intel/2021a'],
        #     'cc': 'mpiicc',
        #     'cxx': 'mpiicpc',
        #     'ftn': 'mpiifort',
        #     #'target_systems': ['vaughan', 'leibniz']
        # },
        {
            'name': 'CUDA',
            'modules': ['CUDA'],
            'cc': 'nvcc',
            'cxx': 'nvcc',
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
