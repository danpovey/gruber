# to be run with python3
"""
This module provides the functions read_wave() and write_wave().  They are fairly thin
convenience wrappers around similar functions from package wavio.
"""

import wavio
import sys
import numpy as np
import math

try:
    from . import file_utils
except:
    import file_utils



def read_wave(f):
    """Reads a wave file as a numpy array of type np.float32.  This is
    based on the wave_io module and just takes care of converting to
    float32.

      Args:
        file: Either a string containing a simple filename, or an
              open file object containing a wave file (which may be
              a pipe, for instance; see ./file_utils.py).
              Caution: it must not have a text I/O wrapper, you may
              need to pass in 'encoding=None' when opening it.

       Returns:

          Returns a pair `(data, samp_rate)` where data` is the wave file as a
          NumPy array with dtype=np.float32 and shape (num_channels,
          num_samples), and `samp_rate` is the sampling frequency in Hz as a
          float.

       Raises:
          Raises various exceptions

    """
    # w will be an object of type wave.Wav_read.
    file = file_utils.open_or_fd(f, encoding=None)
    wav = wavio.read(file)
    # see https://github.com/WarrenWeckesser/wavio/blob/master/wavio.py for
    # format of `wav`

    # we want data as (num_channels, num_samples).. this is the
    # format that seems most compatible with convolutional code and
    # resampling.
    data = wav.data.swapaxes(0, 1)
    if data.dtype == np.int16:
        data = data.astype(np.float32) * (1.0 / 2**15)
    elif data.dtype == np.int24:
        data = data.astype(np.float32) * (1.0 / 2**23)
    else:
        if data.dtype != np.float32:
            raise RuntimeError("Array returned from wavio.read had "
                               "unexpected dtype ".format(data.dtype))
    return (data, float(wav.rate))


def write_wave(data, samp_rate, file):
    """
    Writes a wave file to disk.
    Args:
            data:        A NumPy ndarray of shape (num_channels, num_samples);
                         may have type np.int16 or np.float32 or np.float64.
                         This will be converted to int16 without scaling if possible
                         (i.e. do i = 32768 * f), but if this would exceed the
                         range of int16 it will be scaled down first.
            samp_rate:   The sampling rate of the wave file, in Hz.
                         E.g., 16000.  An int or a float.
            file:        A string or a file object.  If a string, it will
                         be interpreted as a Kaldi rxfilename, i.e. pipes
                         are allowed.
    This function has no return value.  It will raise an exception
    on error.
    """
    if data.dtype != np.float16:
        assert(data.dtype in [np.float32, np.float64])
        if (len(data.shape) < 2 or data.shape[0] > data.shape[1] or
            not data.dtype in [np.float32, np.float64]):
            raise ValueError("Input audio had unexpected type or shape or dtype: {},{}"
                             .format(data.shape, data.dtype))
        max_val = data.max() * 32768.0
        min_val = data.min() * 32768.0

        truncation_scale = 1.0
        if max_val > 32767.0:
            # The + 0.1 below is a small offset to prevent roundoff causing
            # wrap-around errors.
            truncation_scale = 32767.0 / (max_val + 0.1)
        if min_val < -32768.0:
            s = 32768.0 / (-min_val + 0.1);
            if s > truncation_scale:
                truncation_scale = s
        scale = 32768.0 * truncation_scale
        data = np.rint(data * scale).astype(np.int16)
    data = data.swapaxes(0, 1)
    file = file_utils.open_or_fd(file, "w", encoding=None)
    wavio.write(file, data, samp_rate, scale='none')
    file.close()

if __name__ == "__main__":
    for fname in ['/home/dpovey/rm1.wav', '/home/dpovey/rm2.wav', '/home/dpovey/rm.wav' ]:
        (data, rate) = read_wave(fname)
        print("frame-rate={}, shape={}, dtype={}, sum={}, rms={}".format(
            rate, data.shape, data.dtype, data.sum(), math.sqrt((data*data).sum() / data.size)))
    for fname_out in ['/home/dpovey/rm1.wav', '| cat > /home/dpovey/rm2.wav']:
        write_wave(data, rate, fname_out)
