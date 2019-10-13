#!/usr/bin/env python3


import argparse
import lilcom
import gruber.wave_to_numpy as w2n
import gruber.file_utils as file_utils
import os
import numpy as np
import time
from kaldiio import ReadHelper

parser = argparse.ArgumentParser(
    description="Converts phone labels for TIMIT from Kaldi archive to NumPy archive."
    "Note: this reads from stdin which is to be a Kaldi-format archive of integer "
    "vectors, one per phone.")

parser.add_argument("output_file", type=str,
                    help="Output filename, should have .npz suffix")


def main():
    args = parser.parse_args()

    name_to_phones = {}  # from string utterance-id to a NumPy array containing
                         # the phones in 1-based indexing.d
    with ReadHelper('ark:-') as reader:
        for key, numpy_array in reader:
            name_to_phones[key] = numpy_array.astype(np.int8)
    np.savez_compressed(args.output_file, **name_to_phones)




main()
