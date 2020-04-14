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

    # Get all stations
    stations = picks.get_stations(nordic_file_names, config.output_level)

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

        # Check all stations for set day
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
                                trace_file = x[0] + str(x[4].year) + str(x[4].julday) + x[1] + x[2] + x[3]
                                df = trace.stats.sampling_rate
                                # Setup and appli STA/LTA
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
    picks.save_traces(slices, config.save_dir)