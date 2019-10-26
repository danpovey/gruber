
export PYTHONPATH=$PYTHONPATH:/home/dpovey/gruber

timit_root=/home/dpovey/kaldi-clean/egs/timit/s5/

# prepare the audio files as numpy
python3 ./timit_prepare.py $timit_root/data/train/wav.scp b2 c

# Let's get some phone-level labels, just for kicks..

ls /home/dpovey/kaldi-clean/egs/timit/s5/exp/tri3_ali


 pushd $timit_root; . ./path.sh; popd;
 gunzip -c $timit_root/exp/tri3_ali/ali.1.gz | ali-to-phones --per-frame=true $timit_root/exp/tri3_ali/final.mdl ark:- ark,t:- | timit_prepare_phones.py foo.npz


 /home/dpovey/kaldi-clean/egs/timit/s5/exp/tri3_ali

 (
   cd $timit_root
   echo "--num-mel-bins=40" > conf/fbank40.conf

   for d in dev train test; do
     utils/copy_data_dir.sh data/${d} data/${d}_40fbank
     steps/make_fbank.sh --fbank-config conf/fbank40.conf --compress false    data/${d}_40fbank
   done
 )

for d in dev train test; do
  time ./kaldi_to_numpy.py $timit_root/data/${d}_40fbank/feats.scp data/${d}_40fbank.npz
done
