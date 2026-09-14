# CalcUA ReFrame test suite

Wrapper scripts around [ReFrame](https://reframe-hpc.readthedocs.io/en/stable/manpage.html) to run the CalcUA test suite on vaughan, leibniz and breniac and push the results to the database.

Requirements: run the scripts from this repo's checkout, `/apps/antwerpen/reframe/testsuite/calcua-test-suite`, on a login node; ReFrame >= 4.9 (`run_calcua.sh` loads `ReFrame/4.9.1`); membership of `ap_calcua_staff` and of group `vsc20001`, which owns the shared log directory (`run_calcua.sh` sets `umask 002` so files stay group-writable; do the same if you call `reframe` by hand).

## Development Status

In Progress:
- [x] Completion of [issue 3488](https://github.com/reframe-hpc/reframe/issues/3488)
    - Update flexible tests and `daily` mode
- [x] Completion of [issue 3485](https://github.com/reframe-hpc/reframe/issues/3485)
    - Update flask API
- [ ] Completion of [issue 3483](https://github.com/reframe-hpc/reframe/issues/3483)
    - Upgrade Amber tests and improve command line documentation
- [ ] Completion of [issue 3491](https://github.com/reframe-hpc/reframe/issues/3491)
    - Update DB and grafana
- [ ] Completion of [issue 3734](https://github.com/reframe-hpc/reframe/issues/3734)
    - `-p/--prgenv` has no effect when `--mode` is used; until fixed use `-S valid_prog_environs=...`

TODOs:
- [ ] Compile HPCC with toolchains >= 2023a


## Scripts

Both shell scripts take `--help`.

- **`./run_calcua.sh [--push-mongo] [reframe options]`** — runs the suite on the cluster you are logged in to.
  - loads `ReFrame/4.9.1` and points it at `calcua_config.py`
  - every other option is passed to `reframe` unchanged
  - `--push-mongo` runs `push_to_mongo.py` after the run
  - without `--mode`, `--mode=calcua` is used (see [Modes](#modes))

- **`./run.sh [reframe options]`** — runs the suite on all clusters.
  - `git pull`s this repo
  - ssh'es as the current user to `login1.leibniz`, `login1.vaughan` and `login.breniac`
  - starts `./run_calcua.sh --run --push-mongo <options>` there, detached; nothing is printed

- **`./push_to_mongo.py [report] [endpoint]`** — pushes a report to the database.
  - reads `logs/reports/<report>.json`, default `last-$VSC_INSTITUTE_CLUSTER`
  - POSTs every test case to `https://10.28.239.250:27016/add_<endpoint>/`, default endpoint `reframe`

All output lands in `/apps/antwerpen/reframe/logs/`:

- `output/`, `stage/`, `performance/` — job output, stage directories, performance logs
- `reports/last-<cluster>.json` — report of the last run, this is what gets pushed
- `pushtomongo.logs` — output of `push_to_mongo.py`

Layout of this repo:

- `run_calcua.sh`, `run.sh`, `push_to_mongo.py` — the scripts above
- `calcua_config.py` — ReFrame config: systems, partitions, environments, modes
- `checks/<test>/` — the tests. ReFrame imports every `.py` under `checks/`, so keep helper scripts out of it

The parent directory `/apps/antwerpen/reframe/testsuite/` also holds `cpuburn/`, `highload/`, `HPCC-vaughan/` (manual stress tests, not part of the suite), `test-suite/` (EESSI) and `vsc-test-suite/` (VSC test suite, also contained in `checks/`).

## Tags

Tests are selected by tag: `-t TAG` (regex, e.g. `-t "compilation|cue"`), `-T TAG` excludes. `./run_calcua.sh --mode=all --list-tags` lists them (only for tests valid on the current cluster).

Group tags:

| Tag | Selects |
|---|---|
| `daily` | quick sanity checks: `basic`, `cue`, `micro`, `fs`, `halo`. **Excluded by the default `calcua` mode** |
| `compilation` | tests that compile code: `basic`, `alloc`, `fftw`, `halo`, `hpcc` |
| `performance` | every benchmark (all tests except the `cue`/`micro`/`fs` checks) |
| `massive` | multi-node HPCC runs; excluded by the default `calcua` mode |
| `gpu`, `cpu`, `mpi` | hardware / MPI flavour of a test |
| `1nodes`, `2nodes`, `4nodes` | node count (`namd`, `julia`) |
| `calcua`, `vsc`, `apps` | origin: CalcUA-specific, VSC test suite, application tests |

Test tags:

| Tag | Test |
|---|---|
| `basic` | hello world single-/multi-threaded compilation + execution |
| `alloc` | time to allocate 8192 MB |
| `cue` | `env` environment variables, `tools` tool versions, `fs` filesystem mounts, `job` clean job environment |
| `fs` | filesystem mounts + existence/permissions of `/dev/kfd` on `vaughan:amd` |
| `fftw` | FFTW MPI compilation + execution |
| `halo` | halo cell exchange MPI compilation + execution |
| `hpcc` | HPC Challenge (`leibniz:broadwell` only) |
| `micro` | echo hello job + MPI hello (VSC test suite) |
| `burn` | GPU burn on nvidia partitions |
| `abinit`, `amber`, `gaussian`, `gromacs`, `namd`, `quantumespresso`, `vasp` | application benchmarks, parameterised on module `version` |
| `julia`, `matlab`, `python` (`numpy`) | linear algebra benchmarks |

`pytorch` exists but is disabled (commented out).

## Modes

| `--mode` | Selects |
|---|---|
| `daily` | only tag `daily`, with `--flex-alloc-nodes=1` |
| `calcua` (default) | everything **except** tags `daily` and `massive` |
| `all` | everything |

All modes set the output/stage/perflog/report paths. When selecting tests by hand, use `--mode=all`: with the default mode `-t cue` selects nothing.

## Systems

`--system=<cluster>` or `--system=<cluster>:<partition>`. Tests pick partitions by *feature*: a test valid on `+default` does not run on `zen2`.

| Cluster | Partitions (features) |
|---|---|
| `vaughan` | `login` (login), `default` (cpu, default), `zen2`, `zen3`, `zen3_512` (cpu), `nvidia` (gpu), `amd` (gpu, amd) |
| `leibniz` | `login` (login), `default` (cpu, default), `broadwell`, `broadwell_256` (cpu), `nvidia` (gpu) |
| `breniac` | `login` (login), `default` (cpu, default), `skylake` (cpu) |

Environments: `standard`, `foss-{2023a,2024a,2025a}[_mpi]`, `intel-{2023a,2024a,2025a}[_mpi]`, `CUDA`.

## Most used ReFrame options

| Option | Meaning |
|---|---|
| `-l` / `-r` | list / run the selected tests |
| `-t TAG`, `-T TAG` | select / exclude by tag (regex) |
| `-n NAME` | select by test name (regex) |
| `-p ENV` | **ignored when `--mode` is set** ([issue 3734](https://github.com/reframe-hpc/reframe/issues/3734), up to 4.10.3), and `run_calcua.sh` always sets a mode. Use the next row instead |
| `-S [TEST.]valid_prog_environs=E1,E2` | run only in the listed environments (same for `valid_systems`) |
| `--mode=MODE`, `--system=SYS[:PART]` | mode / system from the config file |
| `-J OPT` | pass an option to Slurm, e.g. `-J reservation=myres` |
| `-S [TEST.]VAR=VAL` | override a test *variable* |
| `-P [TEST.]PARAM=VAL0,VAL1` | override a test *parameter* (ReFrame >= 4.9) |
| `-C FILE` | use another config file |

`-S` sets a variable *before* the test is instantiated, so a test that assigns it in `__init__` or a hook wins. All tests declare `valid_systems`/`valid_prog_environs` at class level except `gromacs`, `cue` tools and `calcua_specific`, which compute them from their parameters and cannot be overridden.

## Use cases

- **I changed the image / Slurm / ... and want to test it on a reservation** — target the nodes with `--system` and `-J`, pick the tests by tag:

    ```bash
    ./run_calcua.sh --run --mode=all --system=vaughan:default -J reservation=myres -t "compilation|cue"
    ```

    Use `default` rather than `zen2`/`zen3`: most `cue`/`basic` tests are only valid on `default`/`login` partitions.

- **I specified a partition, but now there are no tests anymore** — the tests are not valid there (see [Systems](#systems)); overwrite their `valid_systems`:

    ```bash
    ./run_calcua.sh --run --mode=all --system=vaughan:zen3_512 -t halo -S valid_systems='*'
    ```

    The same can happen with the environments: `-S valid_prog_environs=...`. Use `-S`, not `-P`: these are variables, and `-P` would turn them into a parameter.

- **I made a new toolchain and want to test it** — add it as an environment in a derived config, then restrict the tests to it with `-S valid_prog_environs` (`-p` is broken with `--mode`, [issue 3734](https://github.com/reframe-hpc/reframe/issues/3734)):

    ```python
    # myconfig.py, next to calcua_config.py
    from calcua_config import *

    site_configuration['environments'].append(
        {'name': 'foss-2025b_mpi', 'cc': 'mpicc', 'cxx': 'mpicxx', 'ftn': 'mpifort', 'modules': ['foss/2025b'], 'features': ['mpi']})
    cpu_env_list.append('foss-2025b_mpi')   # the cpu partitions reference this list
    ```

    ```bash
    ./run_calcua.sh --run --mode=all --system=vaughan:default -C myconfig.py -t "halo|basic|alloc" -S valid_prog_environs=foss-2025b_mpi
    ```

    `fftw` additionally needs an entry for the new environment in the `flags` table of `checks/fft/fftw_benchmark.py`, otherwise it links without `-lfftw3`. For a non-MPI environment use `cc: gcc`, `cxx: g++`, `ftn: gfortran` and no `features`.

- **I built a new version of an application and want to test it** — override the `version` parameter with `-P <TestClass>.version=<module>` (comma-separated for several):

    ```bash
    ./run_calcua.sh --run --mode=all --system=vaughan:default -n vasp_test -P vasp_test.version=VASP/6.6.1-intel-2025a-dftd4-4.0.2
    ```

    Test classes: `AbinitCheck`, `amber_test`, `amber_gpu`, `GaussianCPUTest`, `GaussianCheck`, `gromacs_test`, `Namd_CPUTest`, `NumpyTest`, `QECheck`, `vasp_test`. Check the selection with `-l` first; to keep a version permanently, add it to the `version = parameter([...], type=str)` line in the test. The `type=str` is what lets `-P` convert the command-line value — keep it when adding new parameterised tests.

    Unfortunately, using software in `/apps/antwerpen/testing/...` is currently not supported.
