#!/bin/bash -x

export NNODES=${SLURM_JOB_NUM_NODES}
export PPN=28
export NTASKS=${SLURM_NTASKS}

export EXECHOME=/apps/antwerpen/benchmarks/HPCC-leibniz
export BMHOME=.

module load calcua/2023a
module load intel/2023a

BASEDIR=${BMHOME}/HPCC_${NNODES}
BINDIR=${EXECHOME}/bin

mkdir -p ${BASEDIR}
cd ${BASEDIR}

HPL_Q=`python -c "\
import math
q=math.ceil(math.sqrt($NTASKS))
while($NTASKS%q!=0):
  q=q+1
print(int(q))"`

HPL_P=`echo $(($NTASKS / $HPL_Q))`

#Memory in GB
let HPL_M=90
HPL_B=192
# PTRANS_FACT=128   # oorspronkelijke waarde script; geen reden waarom aangepast t.o.v. volgende regel...
PTRANS_FACT=32      # setting runs 2017

export OMP_NUM_THREADS=1
export TBB_NUM_THREADS=1
export MKL_MIC_ENABLE=0
export I_MPI_DEBUG=5

export I_MPI_PIN=yes
export I_MPI_PIN_CELL=core
export I_MPI_PIN_DOMAIN=omp
export I_MPI_PIN_MODE=pm
export I_MPI_PIN_ORDER=compact
export I_MPI_PROCESSOR_LIST=allcores:grain=core
export KMP_AFFINITY=verbose,granularity=fine,compact,1,0

#export I_MPI_OFA_ADAPTER_NAME=mlx5_0

HPL_N=`python -c "\
import math
v=int(math.ceil(math.sqrt(${HPL_M} * 2**30 / 8 * ${HPL_P}*${HPL_Q}/${PPN})))
rem = v % (${PTRANS_FACT}*${HPL_B})
if rem == 0:
  print(rem)
print(v+(${PTRANS_FACT}*${HPL_B})-rem)"`

echo "PPN=${PPN}"
echo "HPL_P=${HPL_P}"
echo "HPL_Q=${HPL_Q}"
echo "PTRANS_FACT=${PTRANS_FACT}"
echo "HPL_B=${HPL_B}"
echo "HPL_N=${HPL_N}"

let PTRANS_B=${PTRANS_FACT}*${HPL_B}

echo \
"HPLinpack benchmark input file
Innovative Computing Laboratory, University of Tennessee
HPL.out      output file name (if any)
6            device out (6=stdout,7=stderr,file)
1            # of problems sizes (N)
${HPL_N}     Ns
1            # of NBs
${HPL_B}     NBs
1            PMAP process mapping (0=Row-,1=Column-major)
1            # of process grids (P x Q)
${HPL_P}     Ps
${HPL_Q}     Qs
16.0         threshold
1            # of panel fact
1            PFACTs (0=left, 1=Crout, 2=Right)
1            # of recursive stopping criterium
4            NBMINs (>= 1)
1            # of panels in recursion
2            NDIVs
1            # of recursive panel fact.
1            RFACTs (0=left, 1=Crout, 2=Right)
1            # of broadcast
2            BCASTs (0=1rg,1=1rM,2=2rg,3=2rM,4=Lng,5=LnM,6=Psh,7=Psh2)
1            # of lookahead depth
0            DEPTHs (>=0)
0            SWAP (0=bin-exch,1=long,2=mix)
1           swapping threshold
1            L1 in (0=transposed,1=no-transposed) form
1            U  in (0=transposed,1=no-transposed) form
0            Equilibration (0=no,1=yes)
8            memory alignment in double (> 0)
##### This line (no. 32) is ignored (it serves as a separator). ######
0            Number of additional problem sizes for PTRANS
10000        values of N
0            number of additional blocking sizes for PTRANS
${PTRANS_B}  values of NB" > hpccinf.txt


set -x
srun ${BINDIR}/hpcc 2>&1 | tee hpcc.txt
set -x


echo 'Command Executed. End.'
