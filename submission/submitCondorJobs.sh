#!/bin/bash

if [[ $# -eq 0 ]] ; then
    echo 'First argument, name of sample, is needed. Have a good day :)'
else

    sample=$1

    if [ ! -d condorlogs/ ]; then
        mkdir condorlogs/
    fi

    workingDir=${PWD}
    outputDir=${workingDir}/../histograms/v01/
    if [ ! -d "$outputDir" ]; then
        mkdir -p $outputDir
    fi

    condorFile=${sample}_condorJob
    echo '''universe    =  vanilla
workingDir='${workingDir}'/condorlogs/
##arguments   =  '${sample}'
executable  = $(workingDir)/'${condorFile}'.sh
log         = $(workingDir)/log_'${condorFile}'_$(ClusterId).log
error       = $(workingDir)/log_'${condorFile}'_$(ClusterId)-$(ProcId).err
output      = $(workingDir)/log_'${condorFile}'_$(ClusterId)-$(ProcId).out
initialdir  = '$outputDir'
getenv      =  True
####requirements = (OpSysAndVer =?= "SLCern6")
+JobFlavour = "tomorrow"
queue
    ''' > condorlogs/${condorFile}.sub

    echo '''#!/bin/bash
export X509_USER_PROXY=/afs/cern.ch/user/a/algomez/x509up_u15148
export PATH=/afs/cern.ch/work/a/algomez/miniconda3/bin:$PATH
source activate hepaccelerate_cpu
cd '${workingDir}'/../
echo ${PWD}
PYTHONPATH=hepaccelerate:coffea:. python3 run_analysis.py \
  --filelist /afs/cern.ch/work/d/druini/public/hepaccelerate/datasets/algomez/'${sample}'.txt \
  --sample '${sample}'  \
  --outdir '${outputDir}' \
  --boosted \
  --categories all \
  --cache-location /eos/home-a/algomez/tmpFiles/hepacc/  #/eos/user/d/druini/cache/ \
  # --from-cache
    ''' > condorlogs/${condorFile}.sh

    condor_submit condorlogs/${condorFile}.sub

fi
