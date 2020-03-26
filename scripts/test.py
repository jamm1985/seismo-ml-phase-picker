import os
import obspy.io.nordic.core as nordic_reader
from obspy.core import read
import obspy
import sys
import getopt
import logging
from obspy.core import utcdatetime

import utils.picks_slicing as picks
import utils.seisan_reader as seisan
import utils.converter as converter
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
            logging.info(config.help_message)
            print(config.help_message)
            sys.exit()
        elif opt in ("-s", "--save"):
            config.save_dir = arg
        elif opt in ("-r", "--rea"):
            config.full_readings_path = arg
        elif opt in ("-w", "--wav"):
            config.full_waveforms_path = arg

    # Get all nordic files in REA
    nordic_dir_data = os.walk(config.full_readings_path)
    nordic_file_names = []

    for x in nordic_dir_data:
        for file in x[2]:
            nordic_file_names.append(x[0] + '/' + file)

    # Print all nordic file names
    if config.output_level >= 5:
        logging.info('All nordic files:\n')
        for x in nordic_file_names:
            logging.info(x)

    # Get all archive definitions
    definitions = seisan.read_archive_definitions(config.seisan_definitions_path)

    # Get and process all files with picks
    events_total = 0
    no_picks_total = 0
    with_picks_total = 0
    corrupted_files_total = 0

    if config.output_level >= 5:
        logging.info('Reading S-files:\n')

    for file in nordic_file_names:
        slices = picks.slice_from_reading(file, config.full_waveforms_path, config.slice_duration, config.output_level)
        if slices != -1:
            picks.save_traces(slices, config.save_dir)
