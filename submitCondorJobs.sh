#!/bin/bash

if [[ $# -eq 0 ]] ; then
    echo 'First argument, name of sample, is needed. Have a good day :)'
else

    sample=$1
    year=$2

    if [ ! -d condorlogs/ ]; then
        mkdir condorlogs/
    fi

    outputDir=/eos/home-a/algomez/tmpFiles/hepaccelerate/
    if [ ! -d "$outputDir" ]; then
        mkdir -p $outputDir
    fi
    jsonoutputDir=${outputDir}/${year}_private_${sample}
    if [ ! -d "${jsonoutputDir}" ]; then
        mkdir -p $jsonoutputDir
    fi
    workingDir=${PWD}

    if [[ $3 -eq 0 ]] ; then
        queue="queue myfile from samples/${year}_private_${sample}.txt"
        pyOption="--inputfile=\$2"
    else
        queue="queue"
        pyOption="--filelist=${workingDir}/samples/${year}_private_${sample}.txt  "
        #pyOption="--filelist=${workingDir}/samples/${year}_${sample}.txt  "
    fi

    condorFile=${year}_private_${sample}_condorJob
    echo '''universe    =  vanilla
arguments   =  '${sample}' $(myfile) _$(ProcId)
executable  =  '${PWD}'/condorlogs/'${condorFile}'.sh
log         =  '${PWD}'/condorlogs/log_'${condorFile}'_$(ClusterId).log
error       =  '${PWD}'/condorlogs/log_'${condorFile}'_$(ClusterId)-$(ProcId).err
output      =  '${PWD}'/condorlogs/log_'${condorFile}'_$(ClusterId)-$(ProcId).out
initialdir  = '$jsonoutputDir'
#should_transfer_files = YES
#when_to_transfer_output = ON_EXIT
#transfer_input_files = out_'${sample}'.json
getenv      =  True
requirements = (OpSysAndVer =?= "SLCern6")
+JobFlavour = "tomorrow"
'${queue}'
    ''' > condorlogs/${condorFile}.sub

    echo '''#!/bin/bash
export X509_USER_PROXY=/afs/cern.ch/user/a/algomez/x509up_u15148
export PATH=/afs/cern.ch/work/a/algomez/miniconda3/bin:$PATH
source activate hepaccelerate_cpu
cd '${workingDir}'
echo ${PWD}
echo "PYTHONPATH='${workingDir}'/coffea:. python3 '${workingDir}'/myrun_analysis.py --sample=$1 --cache-location='${outputDir}' '${pyOption}' --year='${year}' --boosted"
PYTHONPATH='${workingDir}'/coffea:. python3 '${workingDir}'/myrun_analysis.py --sample=$1 --cache-location='${outputDir}' '${pyOption}' --year='${year}' --boosted
    ''' > condorlogs/${condorFile}.sh

    condor_submit condorlogs/${condorFile}.sub

fi
