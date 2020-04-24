import os
import obspy.io.nordic.core as nordic_reader
from obspy.core import read
from obspy.signal.trigger import plot_trigger
from obspy.signal.trigger import recursive_sta_lta, trigger_onset
import obspy
import sys
import getopt
import logging
import random
import warnings

from obspy.core import utcdatetime
from pprint import pprint

import utils.picks_slicing as picks
import utils.seisan_reader as seisan
import utils.converter as converter
import config.vars as config

# Main function body
if __name__ == "__main__":
    """
    Gets noise slices based on STL/LTA from start_date till end_date in vars.py
    maximum slices number is set in vars.py as max_noise_picks
    """
    # Parse script parameters
    argv = sys.argv[1:]

    try:
        opts, args = getopt.getopt(argv, 'hs:r:l:d:s:e:m:a:', ["help", "save=", "rea=",
                                                               "load=", "output_level=",
                                                               "def=", "start=", "end=",
                                                               "max_picks=", "archives=",
                                                               "offset=", "duration="])
    except getopt.GetoptError:
        logging.error(str(getopt.GetoptError))
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            logging.info(config.noise_help_message)
            print(config.noise_help_message)
            sys.exit()
        elif opt in ("-s", "--save"):
            config.save_dir = arg
        elif opt in ("-r", "--rea"):
            config.full_readings_path = arg
        elif opt in ("-l", "--load"):
            config.stations_load_path = arg
        elif opt == "--output_level":
            config.output_level = int(arg)
        elif opt in ("-d", "--def"):
            config.seisan_definitions_path = int(arg)
        elif opt in ("-s", "--start"):
            string_date = str(arg)
            day = int(string_date[:2])
            month = int(string_date[3:5])
            year = int(string_date[6:])
            config.start_date[0] = year
            config.start_date[1] = month
            config.start_date[2] = day
        elif opt in ("-e", "--end"):
            string_date = str(arg)
            day = int(string_date[:2])
            month = int(string_date[3:5])
            year = int(string_date[6:])
            config.end_date[0] = year
            config.end_date[1] = month
            config.end_date[2] = day
        elif opt in ("-m", "--max_picks"):
            config.max_noise_picks = int(arg)
        elif opt in ("-a", "--archives"):
            config.archives_path = arg
        elif opt == "--offset":
            config.slice_offset = int(arg)
        elif opt == "--duration":
            config.slice_duration = int(arg)

    # Initialize random seed with current time
    random.seed()

    # Get all nordic files in REA
    nordic_dir_data = os.walk(config.full_readings_path)
    nordic_file_names = []

    for x in nordic_dir_data:
        for file in x[2]:
            nordic_file_names.append(x[0] + '/' + file)

    # Get all stations
    # Try to read stations from config/vars.py stations_load_path
    if len(config.stations_load_path) > 0:
        if os.path.isfile(config.stations_load_path):
            stations = []
            f = open(config.stations_load_path, 'r')
            if f.mode == 'r':
                f1 = f.readlines()
                for x in f1:
                    stations.append(x)
            else:
                logging.warning('Cannot open stations file, will form stations manually')
        else:
            logging.warning('Cannot find stations file, will form stations manually')

    # If no stations found, form stations list
    if len(stations) == 0:
        stations = picks.get_stations(nordic_file_names, config.output_level)

    if len(stations) == 0:
        logging.error('No stations found, aborting')
        sys.exit()

    # Get all archive definitions
    definitions = seisan.read_archive_definitions(config.seisan_definitions_path)

    # STA/LTA for archives
    slices = []
    end_date_utc = converter.utcdatetime_from_tuple(config.end_date)

    # Main body TODO: move to utils/
    current_date = config.start_date
    while len(slices) < config.max_noise_picks:
        current_date_utc = converter.utcdatetime_from_tuple(current_date)
        if current_date_utc > end_date_utc:
            break

        # Get all events for current day
        # Get path to s-files folder
        rea_files_path = config.full_readings_path + '/' + str(current_date[0])
        if current_date[1] < 10:
            month_str = '0' + str(current_date[1])
        else:
            month_str = str(current_date[1])

        rea_files_path += '/' + month_str + '/'

        nordic_dir_data = os.walk(rea_files_path)
        nordic_file_names = []

        if current_date[2] < 10:
            day_str = '0' + str(current_date[2])
        else:
            day_str = str(current_date[2])

        for x in nordic_dir_data:
            for file in x[2]:
                if file[:2] == day_str:
                    nordic_file_names.append(x[0] + '/' + file)

        events = picks.get_picks_stations_data(nordic_file_names)

        # If no recorded events happed that day
        if config.tolerate_events_in_same_day or len(events) == 0:
            # ..check all stations for current day
            for station in stations:
                station_archives = seisan.station_archives(definitions, station)

                for x in station_archives:
                    if x[4] <= current_date_utc:
                        if x[5] is not None and current_date_utc > x[5]:
                            continue
                        else:
                            archive_file_path = seisan.archive_path(x, x[4].year, x[4].julday, config.archives_path,
                                                                    config.output_level)
                            if os.path.isfile(archive_file_path):
                                found_archive = True
                                arch_st = read(archive_file_path)
                                for trace in arch_st:
                                    trace_file = x[0] + str(x[4].year) + str(x[4].julday) + x[1] + x[2] + x[
                                        3] + '.NOISE'
                                    df = trace.stats.sampling_rate
                                    # Setup and apply STA/LTA
                                    cft = recursive_sta_lta(trace.data, int(2.5 * df), int(10. * df))
                                    on_of = trigger_onset(cft, 3.5, 0.5)

                                    if len(on_of) > 0:
                                        # Calculate trigger time
                                        start_trace_time = trace.stats.starttime
                                        seconds_passed = float(on_of[0][0]) * float(1.0 / float(df))
                                        start_slice_time = start_trace_time + int(seconds_passed)

                                        time_shift = random.randrange(1, config.slice_offset)
                                        shifted_time = start_slice_time - time_shift
                                        end_time = start_slice_time + config.slice_duration

                                        # Check if this is recorded event
                                        # TODO: Implement with tolerate_events_in_same_day = True

                                        # Slice and store trigger pick
                                        trace_slice = trace.slice(shifted_time, end_time)

                                        slice_name_pair = (trace_slice, trace_file)
                                        slices.append(slice_name_pair)

        # Go to next day and check if it's next month/year
        current_date[2] += 1
        if current_date[2] > config.month_length[current_date[1] - 1]:
            current_date[2] = 1
            current_date[1] += 1
            if current_date[1] > 12:
                current_date[1] = 1
                current_date[0] += 1

    # Save noise slices
    picks.save_traces(slices, config.save_dir, 1)
