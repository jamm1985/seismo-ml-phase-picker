import sys
import getopt
import logging
import random

import config.vars as config
import utils.picks_slicing as picker
import utils.hdf5_composer as hdf5
import utils.utils as utils

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

    # Slices lists
    p_picks = ['P']
    s_picks = ['S']
    n_picks = ['N']

    # Get P and S picks
    p_picks.append(picker.read_picks(config.p_picks_path, 'P'))
    s_picks.append(picker.read_picks(config.s_picks_path, 'S'))

    # Process picks
    p_processed = hdf5.process_pick_list(p_picks)
    s_processed = hdf5.process_pick_list(s_picks)

    # Compose hdf5
    hdf5.compose(config.hdf5_file_name, p_processed, s_processed, s_processed)
