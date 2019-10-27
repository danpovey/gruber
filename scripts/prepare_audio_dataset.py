#!/usr/bin/env python3

"""
This script prepares an audio dataset into a form liked by Gruber, starting
from a Kaldi wav.scp file.  It essentially consists of lilcom-compressing
the files and writing them as npy files, and also outputting some metadata
that can later be read by other utilities.
"""
import argparse
import hashlib
from gruber import file_utils
from gruber import wave_to_numpy
import lilcom
import lilfilter


parser = argparse.ArgumentParser()


parser.add_argument("wav_scp", type=str,
                    help="""A Kaldi wav.scp file with lines of the form:
                    <recording-id> <filename-or-command...>"
                    where any command would be terminated with the pipe symbol (|).
                    """)
parser.add_argument("metadata", type=str,
                    help="""Filename for metadata file to be written.  Will be
                    JSON formatted and contain information about file locations,
                    sample rates, num-channels and sizes, indexed by the
                    recording-ids in the wav.scp""")

parser.add_argument("group-size", type=str, default="1",
                    help="""If you set this to more than one, the files will
                    be grouped in npz arrays (in which they will be indexed
                    by their current recording-ids).  Set this to `all` for
                    all the files in the""")

parser.add_argument("samp-rate", default=None, type=int,
                    help="""If specified, input files will be downsampled to
                    this sampling rate.  (Currently an error will be thrown
                    if the original rate is less than this, as we doubt
                    that would be what you want.""")

parser.add_argument("bits-per-sample", default=8, type=int,
                    help="""The bits per sample used for lilcom compression;
                    must be an integer in the range [4..8]""")

parser.add_argument("md5-order", default=False, action='store_true',
                    help="""For use with the --group-size option... if set,
                    wav-ids will be first be sorted by the strings' md5-hash
                    order, to assure a pseudo-random ordering prior to
                    grouping.""")

parser.add_argument('directories', nargs="+",
                    help="""List of directories where the data is to be stored;
                    should be absolute pathnames.  This program will rotate
                    through these directories when writing data files.
                    """)


def read_and_process_file(rxfilename, samp_rate=None, bits_per_sample=8):
    """
    Reads a wav file from disk, converts to float32, downsamples from whatever sample rate it
    had to `samp_rate` if samp_rate != None, and compresses to a lilcom
    array.
    Args:
         rxfilename:  filename or piped command, in kaldi rxfilename format
         samp_rate:   None if no downsampling is to be done, or the sampling
                      rate we are to downsample to otherwise (as a float or
                      integer)
         bits_per_sample:  The number of bits per sample to use for lilcom
                      compression
    Return:
         On success, returns a tuple (samp_rate, num_samples, data)
         where samp_rate is the sampling rate of the returned data (as an integer),
         num_samples is the number of samples in the compressed file,
         and `data` is the lilcom-compressed audio data, which is a Numpy
         ndarray of shape (num_channels, n) where n depends on the num_samples
          and bits_per_sample.
    Raises:
         Raises whatever errors might come from trying to open the file or pipe,
         including ValueError, FileNotFoundError, SubprocessFailed.
    """
    file = file_utils.open_or_fd(rxfilename)

    (data, in_rate) = wave_to_numpy.read(file)
    if samp_rate != in_rate:
        resampler = lilfilter.Resampler(int(in_rate), int(samp_rate),
                                        dtype=np.float32)


        if samp_rate > rate:
            raise RuntimeError("Currently we are not allowing upsampling "
                               "during data preparation.. this")





def find_groups(ids, md5_order = False, group_size = "1"):
    """
    This function groups a set of recording-ids `ids` into sets.
    """


def md5_sorted(strings):
    """
    This function sorts the strings `strings` in order of their md5 hash values
    (represented as byte strings, not hex strings).  It's used when a
    pseudo-random but deterministic order on string values is desired.

    Args:
       strings:  A list of strings.  Will be encoded with utf-8 before hash values
              are computed.

    """
    pairs = [ (hashlib.md5(x.encode('utf-8')).digest(), x) for x in strings ]
    return [ x[1] for x in sorted(pairs) ]


def as_groups(strings, group_size):
    """
    Takes a list of strings `strings` and returns a list of lists of strings,
    one per 'group'.  The elements of each group will be consecutive elements of
    `strings`.  If group_size can be converted to an integer, aims for the
    groups to each have this size (if "all", it will be all elements).
    """
    try:
        group_size = int(group_size)
    except ValueError:
        group_size = -1
    if group_size <= 0:
        # All strings in one group
        return [ strings ]
    else:
        n = len(strings) / group_size
        r = len(strings) % group_size
        # len_strings = n * group_size + r,
        # so we have r groups of size (group_size + 1)
        # and n-r groups of size (group_size).
        ans = []
        for i in range(n - r):
            # these are of size group_size
            ans.append(strings[i*group_size : (i+1)*group_size])
        offset = group_size * (n - r)
        # `offset` is the start-index of where we begin the groups
        # of size (group_size + 1)..
        for i in range r:
            ans.append(strings[offset + i*(group_size+1):
                               offset + (i+1)*(group_size+1)])
        if True:  # just a check
            s = {}
            for l in ans:
                s = s.union(set(l))
            assert(s == set(strings) and len(strings) == sum([len(x) for x in ans]))
        return ans




## hashlib.md5("hello there".encode('utf-8')).hexdigest()

def main():
    wav_scp_file = open(args.wav_scp, encoding = 'utf-8')
    args = parser.parse_args()

    num_success, num_fail = 0, 0

    recording_ids = []
    reco2rxfilename = { }
    for line in wav_scp_file:
        a = f.split()
        recording_id = a[0]
        rest_of_line = ' '.join(a[1:])
        recording_ids.append(recording_id)
        reco2rxfilename[recording_id] = rest_of_line

    if args.md5_order:
        recording_ids = md5_sorted(recording_ids)

    i = 0
    if args.group_size != "1":
        recording_groups = as_groups(recording_ids, args.group_size)
        for group in recording_groups:
            s,f = process_group(group, reco2rxfilename,
                                directories[i % len(directories)])
            num_success == s
            num_fail += f
            i += 1
            # write this group as npz file
    else:
        for recording in recording_ids:
            try:
                process_recording(recording, reco2rxfilename[recording],
                                  directories[i % len(directories)])
                num_success += 1
            except:
                print("Something went wrong processing recording {}".format(
                    recording))
                num_fail += 1
            i += 1



        try:
            with file_utils.open_or_fd(rest_of_line) as f:

            num_success += 1
        except Exception as e:
            print("Error processing recording-id {}: {}".format(recording_id, e))
            num_fail += 1










if __name__ == "__main__":
    main()
