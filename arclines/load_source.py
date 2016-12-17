""" Module for loading source files
"""
from __future__ import (print_function, absolute_import, division, unicode_literals)

import numpy as np
import json

from astropy.table import Table

import arclines # For path
src_path = arclines.__path__[0]+'/data/sources/'

# Hard-coded string lengths, and more
from arclines import defs
str_len_dict = defs.str_len()
instr_dict = defs.instruments()
lamp_dict = defs.lamps()

def load(src_file, format):
    """
    Parameters
    ----------
    src_file
    format

    Returns
    -------

    """
    # Load
    if format == 'PYPIT1':
        ID_lines, U_lines = load_pypit(1, src_file)
    else:
        raise IOError("Format {:s} for source {:s} is not supported".format(
                format, src_file))
    # Reject lines


def load_pypit(version, src_file):
    """ Load from PYPIT output

    Parameters
    ----------
    version : int
      Flag indicating version of PYPIT output
      1 : JSON format from PYPIT v1

    Returns
    -------
    ID_lines : Table
      Table of arc lines with IDs
    U_lines
      Additional lines

    """
    from pypit import arutils
    # Load
    with open(src_path+src_file,'r') as f:
        pypit_fit = json.load(f)

    npix = len(pypit_fit['spec'])
    # ID lines -- Assumed in NIST if from PYPIT
    ions = np.array(pypit_fit['ions'],
                    dtype='S{:d}'.format(str_len_dict['ion']))
    ID_lines = Table()
    ID_lines['ion'] = ions
    ID_lines['wave'] = pypit_fit['yfit']
    ID_lines['NIST'] = 1
    amps = []
    for jj,xfit in enumerate(pypit_fit['xfit']):
        pix = int(np.round(xfit*(npix-1)))
        amps.append(pypit_fit['spec'][pix])
    ID_lines['amplitude'] = amps

    # Unknown
    # Generate the flag
    uni_ions = np.unique(ions)
    ion_flag = 0
    for uion in uni_ions:
        ion_flag += lamp_dict[uion]

    # Use PYPIT to decode
    wave = arutils.func_val(pypit_fit['fitc'],
                            np.array(pypit_fit['tcent'])/(npix-1),
                            pypit_fit['function'],
                            minv=pypit_fit['fmin'], maxv=pypit_fit['fmax'])
    eamps, extras = [], []
    for kk,iwave in enumerate(wave):
        if np.min(np.abs(ID_lines['wave'].data-iwave)) > 0.5:
            extras.append(iwave)
            pix = int(np.round(pypit_fit['tcent'][kk]))
            eamps.append(pypit_fit['spec'][pix])
    U_lines = Table()
    U_lines['ion'] = str('UNKWN').rjust(str_len_dict['ion'])
    U_lines['wave'] = extras
    U_lines['NIST'] = 0
    U_lines['ion_flag'] = ion_flag
    # Return
    return ID_lines, U_lines

