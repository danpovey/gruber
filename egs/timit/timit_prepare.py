#!/usr/bin/env python3


import argparse
import lilcom
import gruber.wave_to_numpy as w2n
import gruber.file_utils as file_utils
import os
import numpy as np
import time

parser = argparse.ArgumentParser(
    description="Prepares TIMIT data as lilcom-compressed Numpy arrays")

parser.add_argument("input_scp", type=str,
                    help="Input Kaldi scp file of waves, e.g. egs/timit/s5/data/train/wav.scp")
parser.add_argument("output_dir", type=str,
                    help="Directory to write compressed wave files")
parser.add_argument("output_scp", type=str,
                    help="Output file containing <key> <filename> on each "
                    "line; filenames will have suffix .npy.")



def main():
    args = parser.parse_args()

    if not os.path.isdir(args.output_dir):
        raise RuntimeError("Expected directory {} to exist.".format(args.output_dir))
    output_scp_file = open(args.output_scp, "w", encoding="utf-8")

    samp_rate = None


    tot_time_reading = 0.0
    tot_time_compressing = 0.0
    tot_time_writing = 0.0
    n = 0

    with open(args.input_scp, "r", encoding="utf-8") as scp_file:
        for line in scp_file:
            fields = line.split()
            if len(fields) < 2:
                raise RuntimeError("Expected line in {} to have at least two fields, got: {}".format(
                    args.input_scp, line))
            key = fields[0]
            # The rxfilename is the rest of the fields... it may be a command.
            rxfilename = ' '.join(fields[1:])

            filename=(args.output_dir + os.path.sep + key + ".npy")
            print(key, filename, file=output_scp_file)
            if os.path.isfile(filename):
                print("File exists {}, skipping".format(filename))
                continue

            start = time.perf_counter()
            wave_file = file_utils.open_or_fd(rxfilename, encoding=None)
            (f, s) = w2n.read_wave_as_numpy(wave_file)
            tot_time_reading += time.perf_counter() - start

            print("frame-rate={}, shape={}, dtype={}".format(
                f, s.shape, s.dtype))
            if samp_rate is None:
                samp_rate = f
                print("Sampling rate is {}".format(samp_rate))
            elif samp_rate != f:
                print("There is a sampling rate mismatch: {} vs {}".format(
                    samp_rate, s))

            start = time.perf_counter()
            compressed = lilcom.compress(s, axis=0)
            tot_time_compressing += time.perf_counter() - start

            start = time.perf_counter()
            np.save(filename, compressed)
            tot_time_writing += time.perf_counter() - start

            n = n + 1
            if n % 10 == 0:
                print("Tot time reading/compressing/writing is: {},{},{}".format(
                    tot_time_reading, tot_time_compressing, tot_time_writing))

            output_scp_file.flush()
    output_scp_file.close()



main()
