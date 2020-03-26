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
    definitions = seisan.read_archive_definitions(config.seisan_definitions_path)

    for x in definitions:
        print(str(x))