import sys
import getopt
import logging
import utils.hdf5_composer as composer
import utils.utils as utils
import random

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
        files = utils.get_files(config.p_picks_path, 1, 1, r'\.P')
    else:
        files = utils.get_files(config.p_picks_path, 0, 0, r'\.P')

    for file_list in files:
        pick_list = []
        skip = False
        index = -1
        for file in file_list:
            index += 1
            if index >= 3:
                break

            if config.slice_offset_start == 0 and config.slice_offset_end == 0:
                time_shift = 0
            else:
                time_shift = random.randrange(config.slice_offset_start, config.slice_offset_end)

            pick = composer.process(file, rand=time_shift)
            if pick is None:
                skip = True
                break
            pick_list.append([pick, file, file_list[3]])
            if len(pick) != config.required_trace_length:
                skip = True
                break
        if skip:
            continue
        p_picks.append(pick_list)

    # Get S picks
    if config.s_picks_dir_per_event:
        files = utils.get_files(config.s_picks_path, 1, 1, r'\.S')
    else:
        files = utils.get_files(config.s_picks_path, 0, 0, r'\.S')

    for file_list in files:
        pick_list = []
        skip = False
        index = -1
        for file in file_list:
            index += 1
            if index >= 3:
                break

            if config.slice_offset_start == 0 and config.slice_offset_end == 0:
                time_shift = 0
            else:
                time_shift = random.randrange(config.slice_offset_start, config.slice_offset_end)

            pick = composer.process(file, rand=time_shift)
            if pick is None:
                skip = True
                break
            pick_list.append([pick, file, file_list[3]])
            if len(pick) != config.required_trace_length:
                skip = True
                break
        if skip:
            continue
        s_picks.append(pick_list)

    # Get noise picks
    files = utils.get_files(config.noise_picks_hdf5_path, 0, 0, r'\.N', is_noise=True)
    for file_list in files:
        pick_list = []
        skip = False
        index = -1
        for file in file_list:
            index += 1
            if index >= 3:
                break

            if config.slice_offset_start == 0 and config.slice_offset_end == 0:
                time_shift = 0
            else:
                time_shift = random.randrange(config.slice_offset_start, config.slice_offset_end)

            pick = composer.process(file, rand=time_shift, noise=True)
            if pick is None:
                skip = True
                break
            pick_list.append([pick, file, file_list[3]])
            if len(pick) != config.required_trace_length:
                skip = True
                break
        if skip:
            continue
        noise_picks.append(pick_list)

    composer.compose(config.hdf5_file_name, p_picks, s_picks, noise_picks)