import os
import obspy.io.nordic.core as nordic_reader
from obspy.core import read
import obspy
import sys
import getopt
import logging
from obspy.core import utcdatetime
import h5py
import utils.hdf5_composer as composer
import utils.utils as utils

import config.vars as config

# Main function body
if __name__ == "__main__":
    # Parse script parameters
    argv = sys.argv[1:]

    try:
        opts, args = getopt.getopt(argv, 'hs:r:w:', ["help", "save=", "rea=", "wav="])
    except getopt.GetoptError:
        logging.error(str(getopt.GetoptError))
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            logging.info(config.hdf5_creator_help_message)
            print(config.hdf5_creator_help_message)
            sys.exit()

    # Initialize main variables
    p_picks = []
    s_picks = []
    noise_picks = []

    # Get P picks
    if config.p_picks_dir_per_event:
        files = utils.get_files(config.p_picks_path, 1, 1, '*.P*')
    else:
        files = utils.get_files(config.p_picks_path, 0, 0, '*.P*')

    for file in files:
        if len(p_picks) >= config.hdf5_array_length:
            break
        try:
            pick = composer.process(file)
            p_picks.append(pick)
        except Exception:
            continue

    # Get S picks
    if config.s_picks_dir_per_event:
        files = utils.get_files(config.s_picks_path, 1, 1, '*.SP*')
    else:
        files = utils.get_files(config.s_picks_path, 0, 0, '*.S*')

    for file in files:
        if len(s_picks) >= config.hdf5_array_length:
            break
        try:
            pick = composer.process(file)
            s_picks.append(pick)
        except Exception:
            continue

    # Get noise picks
    files = utils.get_files(config.noise_picks_path, 0, 0)
    for file in files:
        if len(noise_picks) >= config.hdf5_array_length:
            break
        try:
            pick = composer.process(file)
            noise_picks.append(pick)
        except Exception:
            continue

    composer.compose(config.hdf5_file_name)
