import os
import sys
import getopt
import logging
import random

import utils.utils as utils
import utils.picks_slicing as picks
import utils.seisan_reader as seisan
import utils.picking_stats as stats

import config.vars as config

# Main body
if __name__ == "__main__":
    # Parse parameters
    argv = sys.argv[1:]

    try:
        opts, args = getopt.getopt(argv, 'hs:r:w:', ["help", "save=", "rea=", "wav="])
    except getopt.GetoptError:
        logging.error(str(getopt.GetoptError))
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            logging.info(config.picks_help_message)
            print(config.picks_help_message)
            sys.exit()
        elif opt in ("-s", "--save"):
            config.save_dir = arg
        elif opt in ("-r", "--rea"):
            config.full_readings_path = arg
        elif opt in ("-w", "--wav"):
            config.full_waveforms_path = arg

    # Initialize random seed with current time
    random.seed()

    # Get file names
    nordic_file_names = utils.get_nordic_files(utils.normalize_path(config.full_readings_path))

    # Get all archive definitions
    definitions = []
    if type(config.seisan_definitions_path) is list:
        for path in config.seisan_definitions_path:
            defs = seisan.read_archive_definitions(path)
            definitions.extend(defs)
    else:
        definitions = seisan.read_archive_definitions(utils.normalize_path(config.seisan_definitions_path))

    # Picking statistics initialization
    stats = stats.PickStats()

    rewrite_duplicates = config.rewrite_duplicates
    last_try_error = False
    last_try_error_id = ""
    last_try_error_file = ""

    try:
        stats.read(utils.normalize_path(config.save_dir) + '/' + config.picking_stats_file)
        if not stats.finished:
            rewrite_duplicates = False
            last_try_error = True
            if type(stats.error_event_id) is str:
                last_try_error_id = stats.error_event_id
            if type(stats.file_currently_parsed) is str:
                last_try_error_file = stats.file_currently_parsed
    except FileNotFoundError as e:
        print("No picking statistics found, starting from anew!")

    if config.explicit_rewrite_duplicates:
        rewrite_duplicates = config.explicit_rewrite_duplicates

    # Picks slicing
    stats.finished = False
    stats.file_currently_parsed = None
    stats.error_event_id = None
    stats.last_run_files_parsed = 0
    stats.last_run_events_parsed = 0
    stats.last_run_phases_parsed = 0

    for file in nordic_file_names:
        stats.file_currently_parsed = file
        error = False

        # Check if file exists
        if not os.path.isfile(file):
            error = True
            err_message = 'no file found! Skipping..'
            print('In file {}: {}'.format(file, err_message))

        # Get event ID
        if not error:
            try:
                event_id = picks.get_event_id(file)
            except UnicodeDecodeError as e:
                error = True
                err_message = str(e)
                print('In file {}: {}'.format(file, err_message))

        if not error and len(event_id) == 0:
            error = True
            err_message = 'no event ID found! Skipping..'
            print('In file {}: {}'.format(file, err_message))

        if not error:
            # Check if event needs to be processed or ignored
            process_event = rewrite_duplicates

            # Process event if it caused error on last try
            if last_try_error and not process_event:
                if file == last_try_error_file or event_id == last_try_error_id:
                    process_event = True

            # Duplicates check
            if not process_event:
                # Check if event not already written
                if not utils.event_exists(utils.normalize_path(config.save_dir) + '/' + event_id):
                    process_event = True

            # Process event
            if process_event:
                # Get picks
                slices = picks.get_picks(file, definitions)

                if slices != -1:
                    # Save picks
                    picks.save_picks(slices, config.save_dir)

                    # Update picking statistics

        # Update&Save picking statistics
        stats.last_file_parsed = stats.file_currently_parsed
        stats.file_currently_parsed = None
        stats.total_files_parsed += 1
        stats.last_run_files_parsed += 1

        stats.write(utils.normalize_path(config.save_dir) + '/' + config.picking_stats_file)
