"""
Provides some Kaldi-like utilities for file I/O
"""

import sys
import subprocess
import re

# Note: this is from Karel's file_io:
# https://github.com/vesis84/kaldi-io-for-python/blob/master/kaldi_io/kaldi_io.py
# but modified for python3.
# You should set encoding=None for binary data.
def open_or_fd(file, mode='r', encoding='utf-8'):
    """ fd = open_or_fd(file)
     Open file, gzipped file, pipe, or forward the file-descriptor.
     Eventually seeks in the 'file' argument contains ':offset' suffix.

     Args:
          mode:  May be 'r' or 'w'.
        encoding:  The file encoding, or None for a binary file.
    """
    offset = None


    #try:
    if True:
        # strip 'ark:' prefix from r{x,w}filename (optional),
        if re.search('^(ark|scp)(,scp|,b|,t|,n?f|,n?p|,b?o|,n?s|,n?cs)*:', file):
            (prefix,file) = file.split(':',1)
        # separate offset from filename (optional),
        if re.search(':[0-9]+$', file):
            (file,offset) = file.rsplit(':',1)
        # input pipe?
        if file[-1] == '|':
            fd = popen(file[:-1], 'r', encoding=encoding)
        # output pipe?
        elif file[0] == '|':
            fd = popen(file[1:], 'w', encoding=encoding)
        # is it gzipped?
        elif file.split('.')[-1] == 'gz':
            fd = gzip.open(file, mode, encoding=encoding)
        # a normal file...
        else:
            fd = open(file, mode)
            #except TypeError:
        # 'file' is opened file descriptor,
        #fd = file
    # Eventually seek to offset,
    if offset != None: fd.seek(int(offset))
    return fd

# based on '/usr/local/lib/python3.6/os.py'
def popen(cmd, mode="r", encoding="utf-8"):
    if not isinstance(cmd, str):
        raise TypeError("invalid cmd type (%s, expected string)" % type(cmd))

    import subprocess, io, threading

    # cleanup function for subprocesses,
    def cleanup(proc, cmd):
        ret = proc.wait()
        if ret > 0:
            raise SubprocessFailed('cmd %s returned %d !' % (cmd,ret))
        return

    # text-mode,
    if mode == "r":
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=sys.stderr)
        threading.Thread(target=cleanup,args=(proc,cmd)).start() # clean-up thread,
        ans = proc.stdout
    elif mode == "w":
        proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stderr=sys.stderr)
        threading.Thread(target=cleanup,args=(proc,cmd)).start() # clean-up thread,
        ans = proc.stdin
    else:
        raise ValueError("invalid mode %s" % mode)

    if encoding != None:
        return io.TextIOWrapper(ans, encoding=encoding)
    else:
        return ans
