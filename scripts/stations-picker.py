import os
import obspy.io.nordic.core as nordic_reader
from obspy.core import read
import obspy
import sys
import getopt
import logging
import random
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

    # Initialize random seed with current time
    random.seed()

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

    # Get all stations
    stations = picks.get_stations(nordic_file_names, config.output_level)

    stations = sorted(stations)
    print('ALL STATIONS')
    print(str(stations))
