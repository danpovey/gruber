# to be run with python3

import wave
import sys
import numpy as np
if __name__ == "__main__":
    try:
        from . import file_utils
    except:
        import file_utils



def read_wave_as_numpy(f):
    """
    Reads a wave file as a numpy array:

      Args:
        file: Either a string containing a simple filename, or an
              open file object containing a wave file (which may be
              a pipe, for instance; see ./file_utils.py).
              Caution: it must not have a text I/O wrapper, you may
              need to pass in 'encoding=None' when opening it.

       Returns:
          Returns a pair (f, a) where f is the sampling frequency as a
          float and a is the wave file as a NumPy array with shape
          (num_samples, num_channels).  The dtype of a will be either
          int16 (if the wave file was 16-bit pcm) or float32 if
          the wave file was 24-bit pcm or 32-bit float.
       Raises:
          Raises various exceptions
    """
    # w will be an object of type wave.Wav_read.
    w = wave.open(f, mode='rb')

    (num_channels, samp_width, frame_rate, num_frames,
     compression_type, compression_name) = w.getparams()

    assert compression_type == 'NONE'
    if num_frames == 0:
        raise RuntimeError("No frames in file")

    read_bytes = w.readframes(num_frames)
    num_frames_read = len(read_bytes) // int(samp_width * num_channels)
    if num_frames_read != num_frames:
        print("Reading {}, num-frames differs {} in header vs. {} read".format(
            filename, num_frames, num_frames_read), f=sys.stderr)


    if samp_width != 2:
        #  Unfortunately python's wave module really sucks and crashed
        #  for me while reading 24-bit pcm input; it doesn't seem to
        #  even want to handle floating point.
        raise RuntimeError("Unexpected sample width {}".format(samp_width))

    samples = np.ndarray(shape=(num_frames_read, num_channels),
                         dtype='<i2', buffer=read_bytes)
    if sys.byteorder == 'big':
        samples = samples.astype('>i{}'.format(samp_width))
    return (frame_rate, samples)

if __name__ == "__main__":
    fname = '/home/dpovey/rm.wav'
    (f, s) = read_wave_as_numpy(fname)
    print("frame-rate={}, shape={}, dtype={}, sum={}".format(
        f, s.shape, s.dtype, s.sum()))
