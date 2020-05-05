# -*- coding: utf-8 -*-
#!/usr/bin/python

import os, subprocess

def _qx(cmd, verbose=False):
    # naive version of qx() is not portable to Windows
    if verbose: print(cmd)
    output = os.popen(cmd + ' 2>/dev/null').read()
    return output

def qx(cmd, verbose=False):
    '''Just like qx// or backticks operator from Perl, running the command
    and returning the STDOUT results as a string.  Optional echo of the
    command issued first.
    '''
    if verbose: print(cmd)
    run = subprocess.Popen(cmd, shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    (out, err) = run.communicate()
    if run.returncode != 0:
        return 'Return code: %d' % run.returncode
    return out

def system(cmd, verbose=False):
    '''Just like os.system() but with optional echo of the command.'''
    if verbose: print(cmd)
    return os.system(cmd)
    
