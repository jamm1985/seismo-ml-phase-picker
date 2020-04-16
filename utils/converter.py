import os
import sys
import obspy.io.nordic.core as nordic_reader
from obspy.core import read
from obspy.core import utcdatetime
import logging


def utcdatetime_from_string(string):
    """
    Converts string of formats: YYYYMMDD, YYYYMMDDHHmm, YYYYMMDDHHmmss to obspy.core.utcdatetime.UTCDateTime
    :param string: string   datetime string of either formats: YYYYMMDD, YYYYMMDDHHmm, YYYYMMDDHHmmss
    :return:       obspy.core.utcdatetime.UTCDateTime
                   None     - conversion failed
    """
    if len(string) in [8, 14]:
        return utcdatetime.UTCDateTime(string)
    elif len(string) == 12:
        new_string = string + "00"
        return utcdatetime.UTCDateTime(new_string)
    return None


def utcdatetime_from_tuple(date):
    """
    Creates obspy.core.utcdatetime.UTCDateTime from tuple of integers like (year, month, day)
    :param date:
    :return:
    """
    line = str(date[0])
    if date[1] < 10:
        line += '0'
    line += str(date[1])
    if date[2] < 10:
        line += '0'
    line += str(date[2])
    return utcdatetime_from_string(line)
