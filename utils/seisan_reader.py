import os
import sys
import obspy.io.nordic.core as nordic_reader
from obspy.core import read
from obspy.core import utcdatetime
import logging

import utils.converter as converter
import utils.picks_slicing as picks


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
    :return: [(string, string, string, string, UTCDateTime, UTCDateTime)] - list of tuples like (station, channel,
                                                                            subdir, location, start date, end date)
                                                                            end date might be None if absent (if archive
                                                                            still continues)
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
        channel = instances[2][0:3]
        subdir = instances[2][3:5]
        location = instances[2][5:7]
        start_date = converter.utcdatetime_from_string(instances[3])

        if len(instances) == 5:
            end_date = converter.utcdatetime_from_string(instances[4])

            data_tuple = (station, channel, subdir, location, start_date, end_date)
        else:
            data_tuple = (station, channel, subdir, location, start_date, None)

        return data_tuple

    return None


def archive_path(archive_definition, year, day, archive_dir='', output_level=0):
    """
    Returns path in archives dir to an archive file
    archive_definition format: (station, channel, subdir, location, start date, end date)
    :param archive_definition: tuple        - archive definition tuple (see archive_def method)
    :param year:               string/int   - year of record
    :param day:                string/int   - day of record
    :param archive_dir:        string       - path to archive directories, empty by default
    :param output_level:       int          - 0 - min output, 5 - max output, default - 0
    :return:                   string       - partial path of archive record (path to archive directory
                                              itself can be found in config/vars.py)
    """
    if day is int and day > 365 and output_level >= 0:
        logging.warning("In archive_path: day value is bigger than 365")

    # Subdirectories:
    path = archive_definition[2] + '/' + archive_definition[0] + '/'
    # Record file:
    path += archive_definition[0] + '.' + archive_definition[2] + '.'  # station.subdir.
    path += archive_definition[3] + '.' + archive_definition[1] + '.'  # location.channel

    year_str = str(year)
    while len(year_str) != 4:
        year_str = '0' + year_str
    path += year_str + '.'

    day_str = str(day)
    while len(day_str) != 3:
        day_str = '0' + day_str
    path += day_str

    if len(archive_dir) != 0:
        return picks.normalize_path(archive_dir) + '/' + path

    return path

