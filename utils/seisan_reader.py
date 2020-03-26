import os
import sys
import obspy.io.nordic.core as nordic_reader
from obspy.core import read
from obspy.core import utcdatetime
import logging

import utils.converter as converter

def read_archive_definitions(reading_path, output_level=0):
    """
    Reads SEISAN DEFINITIONS file and returns all archive definitions tuples list
    :param reading_path: string     path to definitions file
    :param output_level: int        0 - min output, 5 - max output, default - 0
    :return: [(string, string, string, string, UTCDateTime, UTCDateTime)] - list of tuples like (station, channel, subdir, location, start date, end date)
                                                                            - end date might be None if absent (if archive still continues)
             -1                                                           - error
    """
    f = open(reading_path, "r")
    if f.mode != 'r':
        if output_level >= 0:
            logging.error("Can't open seisan def file: " + reading_path)
        return -1

    content = f.readlines()
    data = []
    for x in content:
        data_tuple = archive_def(x)

        if data_tuple is not None:
            data.append(data_tuple)

    return data

def find_station_archive_definitions(reading_path, station_name, output_level=0):
    """
    Reads SEISAN DEFINITIONS file and returns all station archives definitions
    :param reading_path: string     path to definitions file
    :param station_name: string     name of the station
    :param output_level: int        0 - min output, 5 - max output, default - 0
    :return: [(string, string, string, string, UTCDateTime, UTCDateTime)] - list of tuples like (station, channel, subdir, location, start date, end date)
                                                                          - end date might be None if absent (if archive still continues)
             -1                                                           - error
    """
    f = open(reading_path, "r")
    if f.mode != 'r':
        if output_level >= 0:
            logging.error("Can't open seisan def file: " + reading_path)
        return -1

    content = f.readlines()
    data = []
    for x in content:
        data_tuple = archive_def(x)

        if data_tuple is not None and data_tuple[0] == station_name:
            data.append(data_tuple)

    return data


def archive_def(definition_line):
    """
    Converts seisan archive definition string to a tuple (string, string, string, string, UTCDateTime, UTCDateTime)
    which means (station, channel, subdir, location, start date, end date)
    :param definition_line: string      archive definition line
    :return: (string, string, string, string, UTCDateTime, UTCDateTime)
                                        - archive definition tuple
                                        (station, channel, subdir, location, start date, end date)
             None                       - if line is not an station archive definition
    """
    instances = definition_line.split()
    if len(instances) in [4, 5] and instances[0] == "ARC_CHAN":
        station = instances[1]
        channel = instances[2][0:2]
        subdir = instances[2][3:4]
        location = instances[2][5:6]
        start_date = converter.utcdatetime_from_string(instances[3])

        if len(instances) == 5:
            end_date = converter.utcdatetime_from_string(instances[4])

            data_tuple = (station, channel, subdir, location, start_date, end_date)
        else:
            data_tuple = (station, channel, subdir, location, start_date, None)

        return data_tuple

    return None
