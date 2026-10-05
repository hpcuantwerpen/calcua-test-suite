# CalcUA ReFrame test suite

[ReFrame](https://reframe-hpc.readthedocs.io/en/stable/manpage.html) tests for vaughan, leibniz and breniac, with scripts to run them and push the results to the database.

```bash
./run_calcua.sh --mode=all --list-tags            # tags available here
./run_calcua.sh --mode=all -l -t compilation      # list what would run
./run_calcua.sh --run --mode=all -t compilation   # run it
```

## Requirements

- a checkout on a login node, cloned with `--recurse-submodules`. Production: `/apps/antwerpen/reframe/testsuite/calcua-test-suite`
- ReFrame >= 4.9 (`run_calcua.sh` loads `ReFrame/4.9.1`)
- membership of `ap_calcua_staff` (Slurm account)
- membership of `vsc20001` (owns the shared log directory), unless you set `CALCUA_LOGDIR`

## Scripts

**`./run_calcua.sh [--push-mongo] [reframe options]`** — runs on the current cluster. Passes all options to `reframe`, adding:

- `--mode=default` if no `--mode` is given
- `--module-mappings module_mappings.txt` if none is given
- a per-cluster lock: a second run with the same `CALCUA_LOGDIR` waits for the first
- `umask 002`, so the shared logs stay group-writable

`--push-mongo` runs `push_to_mongo.py` afterwards.

**`./run.sh [reframe options]`** — pulls the production checkout, then starts `run_calcua.sh --run --push-mongo <options>` detached on `login1.leibniz`, `login1.vaughan` and `login.breniac`.

**`./push_to_mongo.py [report] [endpoint]`** — POSTs every test case in `$CALCUA_LOGDIR/reports/<report>.json` (default `last-<cluster>`) to `https://service.antwerpen.vsc:27016/add_<endpoint>/` (default `reframe`). HTTP errors are not checked.

**Output** goes to `$CALCUA_LOGDIR`, default `/apps/antwerpen/reframe/logs/`; `run.sh` forwards it. Use e.g. `CALCUA_LOGDIR=$VSC_DATA/reframe/logs` to stay out of the shared directory.

| Path | Content |
|---|---|
| `output/`, `stage/`, `performance/` | job output, stage dirs, perf logs |
| `reports/last-<cluster>.json` | last report; this is what gets pushed |
| `pushtomongo.logs` | `push_to_mongo.py` output |

## Selecting tests

`-t TAG` selects, `-T TAG` excludes, `-n NAME` selects by class name; all are regexes.

| `--mode` | Runs |
|---|---|
| `default` | everything except `massive` |
| `all` | everything |

| Group tag | Tests |
|---|---|
| `calcua` / `vsc` | `checks/` / `vsc-test-suite/tests/` |
| `apps` | openfoam, flame, namd, julia, matlab, numpy. **Not** abinit, amber, gaussian, gromacs, QE, vasp |
| `compilation` | basic (CalcUA), alloc, fftw, halo, hpcc |
| `performance` | all except basic, cue, micro and CalcUA fs |
| `massive` | hpcc 24 nodes, openfoam 64M |
| `gpu` | amber_gpu, gromacs GPU, burn, GPU micro jobs |
| `cpu` | amber_test only |
| `mpi` | halo, MPI hello only |
| `1nodes` `2nodes` `4nodes` | namd (1/2/4), julia (1) |

| Test tag | Test |
|---|---|
| `basic` | CalcUA hello world (C, C++, threaded); VSC echo job |
| `alloc` | allocate 8192 MB |
| `cue` | VSC environment checks: `env`, `tools`, `fs` (mounts), `job` |
| `fs` | cue mounts + `/dev/kfd` on `vaughan:amd` |
| `micro` | VSC echo job, MPI hello, GPU job |
| `fftw`, `halo` | MPI compile + run |
| `hpcc` | HPC Challenge, 1/8/24 nodes, `leibniz:broadwell` only |
| `burn` | GPU burn, non-deprecated nvidia |
| `openfoam` | cavity3D (`icoFoam`, mesh 1M/8M/64M), needs an **ESI** module (`v2506`); also matches `flame` |
| `flame` | counterFlowFlame2D, 2 nodes, needs an **openfoam.org** module (`13`; 11/12 work, 10 doesn't). Scale with `-S mesh_scale=N` |
| `abinit` `amber` `gaussian` `gromacs` `quantumespresso` `vasp` | app benchmarks, parameterised on `version` |
| `namd`, `julia`, `matlab`, `numpy` | VSC app benchmarks |

## Where tests run

`--system=CLUSTER[:PARTITION]`. Tests select partitions by feature.

| Cluster | Partitions (features) |
|---|---|
| `vaughan` | `login` (cpu login), `default` (cpu default), `zen2` `zen3` `zen3_512` (cpu), `nvidia` (gpu nvidia), `amd` (gpu amd) |
| `leibniz` | `login` (cpu login), `default` (cpu default), `broadwell` `broadwell_256` (cpu), `nvidia` (gpu nvidia deprecated) |
| `breniac` | `login` (cpu login), `default` (cpu default), `skylake` (cpu) |

Environments: `standard` (no modules), `foss-`/`intel-{2023a,2024a,2025a}`, their `_mpi` variants (features `mpi fftw`), `CUDA`. Login and AMD partitions have only `standard`.

## Changing the software under test

| Test loads | Tool |
|---|---|
| a `version` parameter: abinit, amber, gaussian, gromacs, QE, vasp, openfoam, flame | `-P Class.version=MOD[,MOD]` |
| a bare name (`NAMD`, `Julia`, `MATLAB`, `SciPy-bundle`, ...): VSC suite | `-M 'NAME:NAME/VERSION'` |
| an environment's toolchain: compiled tests | a new environment, see below |
| modules in its own script: HPCC | edit `checks/HPCC/src/` |
| software in `/apps/antwerpen/testing/` | not supported yet |

| Caveat | |
|---|---|
| `-M` on a `version` test | matches only the exact name: `-M 'VASP:...'` does nothing; a full-name mapping mislabels the report |
| `gromacs_test` | CUDA builds on GPU (1 node), others on CPU (8 nodes) |
| `module_mappings.txt` | applies to **every** run, production included (currently `NAMD`). `-M` adds to it; `--module-mappings /dev/null` disables it |

## ReFrame options

| Option | Meaning |
|---|---|
| `-l` / `-r` | list / run |
| `-t` `-T` `-n` | select by tag, exclude by tag, select by name |
| `--system=SYS[:PART]` | target cluster/partition |
| `-J OPT` | Slurm option, e.g. `-J reservation=myres` |
| `-S [TEST.]VAR=VAL` | set a variable (`valid_systems`, `valid_prog_environs`, `mesh_scale`). No effect on `valid_systems` of `gromacs_test`, `calcua_specific`, VSC `cue/tools` |
| `-P [TEST.]PARAM=V1,V2` | set a parameter (`version`). Needs `type=` on the parameter; never use it for `valid_*` |
| `-M`, `--module-mappings` | swap modules |
| `-C FILE` | other config file |
| `-p ENV` | **broken with `--mode`** ([#3734](https://github.com/reframe-hpc/reframe/issues/3734)); use `-S valid_prog_environs=ENV` |

## Examples

Run on the login node of the cluster you target; `--system` cannot reach another cluster.

### Look before you run

```bash
./run_calcua.sh --mode=all --list-tags                              # tags of tests valid on this cluster
./run_calcua.sh --mode=all -l                                       # every test and its variants
./run_calcua.sh --mode=all -l -t gpu --system=vaughan:nvidia        # what runs on one partition
./run_calcua.sh --mode=all -l -t performance -T "gpu|massive"       # select, then exclude
./run_calcua.sh --mode=all --dry-run -n HaloCellExchange            # generate job scripts in stage/, submit nothing
```

### Routine runs

```bash
./run_calcua.sh --run                                 # this cluster, mode default (no massive)
./run_calcua.sh --run --push-mongo                    # same, then push the report
./run.sh                                              # every cluster, detached, pushes
./run.sh --mode=all -t "compilation|cue"              # every cluster, a subset
```

`run.sh` pulls the production checkout: commit and push your changes first.

### Keep a run out of the shared logs

```bash
mkdir -p $VSC_DATA/reframe/logs
CALCUA_LOGDIR=$VSC_DATA/reframe/logs ./run_calcua.sh --run --mode=all -t basic
CALCUA_LOGDIR=$VSC_DATA/reframe/logs ./push_to_mongo.py      # push that report, if wanted
```

The directory must exist: the lock file is created in it.

### Select precisely

```bash
./run_calcua.sh --run --mode=all -n HaloCellExchange                                   # one test class
./run_calcua.sh --run --mode=all -n HaloCellExchange -P HaloCellExchange.launcher=srun # one variant
./run_calcua.sh --run --mode=all -n HaloCellExchange -S valid_prog_environs=foss-2025a_mpi
./run_calcua.sh --run --mode=all -n OpenFOAMCavity3DCheck -P OpenFOAMCavity3DCheck.mesh=1M
./run_calcua.sh --run --mode=all -n vasp_test -P vasp_test.num_nodes=4
```

### Test a reservation or changed nodes

```bash
./run_calcua.sh --run --mode=all --system=vaughan:default -J reservation=myres -t "compilation|cue"
./run_calcua.sh --run --mode=all --system=vaughan:default -J reservation=myres -t "compilation|cue|micro|apps"
./run_calcua.sh --run --mode=all --system=vaughan:default -J nodelist=<node> -t "basic|cue"
```

Use `default`, not `zen2`/`zen3`: most `cue`/`basic` tests only run on `default`/`login`.

### No tests on my partition

```bash
./run_calcua.sh --run --mode=all --system=vaughan:zen3_512 -t halo -S valid_systems='*'
./run_calcua.sh --run --mode=all --system=vaughan:zen3 -n vasp_test -S vasp_test.valid_systems='*'
./run_calcua.sh --run --mode=all --system=vaughan:zen2 -t basic -S valid_prog_environs='*'
```

Always name the partition: `'*'` also matches login nodes.

### GPU nodes

```bash
./run_calcua.sh --run --mode=all --system=vaughan:nvidia -t gpu      # amber, gromacs, burn, GPU job
./run_calcua.sh --run --mode=all --system=vaughan:nvidia -t burn
./run_calcua.sh --run --mode=all --system=vaughan:amd -t "fs|micro"  # /dev/kfd check, AMD GPU job
```

### Massive tests

```bash
./run_calcua.sh --run --mode=all -t massive                                         # hpcc 24 nodes (leibniz), openfoam 64M
./run_calcua.sh --run --mode=all -n HPCCTest -P HPCCTest.num_nodes=24               # on leibniz
./run_calcua.sh --run --mode=all -n OpenFOAMCavity3DCheck -P OpenFOAMCavity3DCheck.mesh=64M
```

`--mode=default` hides these even when selected by name.

### New application build

```bash
./run_calcua.sh --run --mode=all -n vasp_test -P vasp_test.version=VASP/6.6.1-intel-2025a-dftd4-4.0.2
./run_calcua.sh --run --mode=all -n QECheck -P QECheck.version=QuantumESPRESSO/7.4-foss-2024a,QuantumESPRESSO/<new>
./run_calcua.sh --run --mode=all -n AbinitCheck -P AbinitCheck.version=ABINIT/<version>
./run_calcua.sh --run --mode=all -n amber_gpu -P amber_gpu.version=Amber/<version>-CUDA-<cuda>
./run_calcua.sh --run --mode=all -n GaussianCheck -P GaussianCheck.version=Gaussian/<version>
./run_calcua.sh --run --mode=all -n gromacs_test -P gromacs_test.version=GROMACS/2025.3-foss-2025a          # CPU, 8 nodes
./run_calcua.sh --run --mode=all -n gromacs_test -P gromacs_test.version=GROMACS/<version>-CUDA-<cuda>       # GPU, 1 node
./run_calcua.sh --run --mode=all -n OpenFOAMCavity3DCheck -P OpenFOAMCavity3DCheck.version=OpenFOAM/<v25xx>-foss-<tc>   # ESI
./run_calcua.sh --run --mode=all -n OpenFOAMCounterFlowFlame2DCheck -P OpenFOAMCounterFlowFlame2DCheck.version=OpenFOAM/<11|12|13>-foss-<tc>  # openfoam.org
```

The version replaces the default list; list both to compare old and new in one run.

### New build of a VSC-suite application

```bash
./run_calcua.sh --run --mode=all -n Namd_CPUTest -M 'NAMD:NAMD/<version>'
./run_calcua.sh --run --mode=all -n JuliaLinalgTest -M 'Julia:Julia/<version>'
./run_calcua.sh --run --mode=all -n "Namd|Julia" -M 'NAMD:NAMD/<version>' -M 'Julia:Julia/<version>'
./run_calcua.sh --run --mode=all -n Namd_CPUTest --module-mappings /dev/null       # site default, ignoring module_mappings.txt
```

For a permanent swap, edit `module_mappings.txt`: it applies to production runs.

### Scale a test

```bash
./run_calcua.sh --run --mode=all -n OpenFOAMCounterFlowFlame2DCheck -S mesh_scale=10   # 1000 x 400 cells
./run_calcua.sh --run --mode=all -n Namd_CPUTest -t 4nodes                          # pick a node count by tag
```

### Rerun failures, debug

```bash
./run_calcua.sh --run --restore-session=$CALCUA_LOGDIR/reports/last-$VSC_INSTITUTE_CLUSTER.json --failed
./run_calcua.sh --run --mode=all -n HaloCellExchange --keep-stage-files            # keep stage/ after success
ls $CALCUA_LOGDIR/output/vaughan/default/                                           # job output per system/partition
```

The rerun overwrites `last-<cluster>.json`; don't `--push-mongo` a partial rerun.

### New toolchain

Add an environment in a derived config:

```python
# myconfig.py, next to calcua_config.py
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from calcua_config import *

site_configuration['environments'].append(
    {'name': 'foss-2025b_mpi', 'cc': 'mpicc', 'cxx': 'mpicxx', 'ftn': 'mpifort', 'modules': ['foss/2025b'], 'features': ['mpi', 'fftw']})
cpu_env_list.append('foss-2025b_mpi')
```

```bash
./run_calcua.sh --run --mode=all --system=vaughan:default -C myconfig.py -t "halo|basic|alloc|fftw" -S valid_prog_environs=foss-2025b_mpi
```

```bash
./run_calcua.sh --run --mode=all --system=vaughan:default -C myconfig.py -t "basic|alloc" -S valid_prog_environs=foss-2025b     # non-MPI env, if added
```

`fftw` also needs an entry in the `flags` table of `checks/fft/fftw_benchmark.py`. A non-MPI environment uses `cc: gcc`, `cxx: g++`, `ftn: gfortran` and no `features`.

## Repository layout

| Path | Content |
|---|---|
| `calcua_config.py` | systems, partitions, environments, modes |
| `module_mappings.txt` | mappings for every run |
| `checks/` | CalcUA tests. Every `.py` here is imported: no helper scripts |
| `vsc-test-suite/` | [VSC test suite](https://github.com/Lewih/vsc-test-suite), pinned submodule. Update: `git submodule update --remote vsc-test-suite`, commit the pointer |
| `../cpuburn/`, `../highload/`, `../HPCC-vaughan/`, `../test-suite/` | manual stress tests and EESSI, not part of the suite |

### Vendored third-party test cases

| Case | Source | Licence + local deviations |
|---|---|---|
| `checks/openfoam/src/cavity3D/` | [OpenFOAM HPC TC](https://develop.openfoam.com/committees/hpc/-/tree/develop/incompressible/icoFoam/cavity3D); pipeline after [EESSI](https://github.com/EESSI/test-suite) | CC BY-SA 4.0, `COPYING` |
| `checks/openfoam/src/counterFlowFlame2D/` | [OpenFOAM-13 tutorial](https://github.com/OpenFOAM/OpenFOAM-13/tree/master/tutorials/multicomponentFluid/counterFlowFlame2D) | GPL-3.0, `COPYING` |

Update by re-copying from upstream, not by hand.
