
export PYTHONPATH=$PYTHONPATH:/home/dpovey/gruber

timit_root=/home/dpovey/kaldi-clean/egs/timit/s5/

# prepare the audio files as numpy
python3 ./timit_prepare.py $timit_root/data/train/wav.scp b2 c

# Let's get some phone-level labels, just for kicks..

ls /home/dpovey/kaldi-clean/egs/timit/s5/exp/tri3_ali


  pushd $timit_root; . ./path.sh; popd;
 gunzip -c $timit_root/exp/tri3_ali/ali.1.gz | ali-to-phones --per-frame=true $timit_root/exp/tri3_ali/final.mdl ark:- ark,t:- | timit_prepare_phones.py foo.scp
