import os
import obspy.io.nordic.core as nordic_reader
from obspy.core import read
import obspy
import sys
import getopt
import logging
from obspy.core import utcdatetime
import h5py

import config.vars as config

test_hdf5_file_path = "/home/chernykh/model_pol_best.hdf5"

f = h5py.File(test_hdf5_file_path, 'r')
print(str(list(f.keys())))