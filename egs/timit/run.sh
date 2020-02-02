

export GRUBER_ROOT=$(dirname $(dirname $(pwd)))
export PYTHONPATH=$PYTHONPATH:$GRUBER_ROOT
UTILS=$GRUBER_ROOT/scripts/utils

timit=/export/corpora5/LDC/LDC93S1/timit/TIMIT

set -e
local/timit_data_prep.sh
# the above script prepares data/raw/{train,dev,test}_wav.scp


timit_root=/home/dpovey/kaldi-clean/egs/timit/s5/
# dirs is where we will put the compressed wave data.
dirs=( /export/b{17,18,19}/dpovey/gruber/timit_audio )
for dir in $dirs; do  mkdir -p $dir; done



# change the following to run.pl if you don't have GridEngine
if command -v qsub; then
  cmd="$UTILS/parallel/queue.pl"
else
  cmd="$UTILS/parallel/run.pl"
fi


nj=10
for data in train dev test; do
  if [ -f data/${data}/manifest.json ]; then
    echo "$0: not preparing data/${data}/manifest.json since it already exists"
  else
    echo "$0: Preparing audio for $data set *** "
    mkdir -p data/${data}/log
    $cmd JOB=1:$nj data/${data}/log/prepare_audio.JOB.log \
         python3 $GRUBER_ROOT/scripts/data/prepare_audio_dataset.py --num-jobs=$nj --job=JOB \
         $timit_root/data/${data}/wav.scp data/${data}/manifest.JOB.json ${dirs[*]}
    $GRUBER_ROOT/scripts/manifest/merge_manifests.py \
      data/${data}/manifest.*.json data/${data}/manifest.json
    rm data/${data}/manifest.*.json
  fi
done
