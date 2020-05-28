import os
import sys
import obspy.io.nordic.core as nordic_reader
from obspy.core import read
import logging
import random
import utils.seisan_reader as seisan
import config.vars as config
from pathlib import Path
from obspy.io.mseed import InternalMSEEDError
from obspy.signal.trigger import recursive_sta_lta, trigger_onset
from pprint import pprint
import obspy.core.utcdatetime


def compose(filename, p_picks, s_picks, noise_picks):
    """
    Composes an hdf5 file from processed data
    :param filename:    string - full name of resulting hdf5 file
    :param p_picks:     list   - list of processes p-wave picks
    :param s_picks:     list   - list of processes s-wave picks
    :param noise_picks: list   - list of processes noise picks
    :return:
    """
    return None


def process(filename, file_format="MSEED"):
    """
    Processes a pick file to be suitable for hdf5 packing
    :param filename:    string - filename
    :param file_format: string - format of the file, default: miniSEED "MSEED"
    :return: list of samples
    """
    st = read(filename, file_format)

    # Resampling
    if st[0].stats.sampling_rate != config.required_df:
        resample(st)

    # Detrend
    if config.detrend:
        st.detrend(type='linear')

    # High-pass filtering
    if config.highpass_filter_df > 1:
        st.filter("highpass", freq=config.highpass_filter_df)

    # Normalize
    st.normalize(global_max=config.global_max_normalizing)

    # Check that size is accurate
    resize(st, config.required_trace_length)

    return st[0].data

def resample(stream, df):
    """
    Resamples trace to required sampling rate
    :param trace: trace to resample
    :param df:
    :return:
    """
    stream.resample(df)

def resize(stream, size):
    """
    Cuts list of data size
    :param data:
    :return:
    """
    if len(stream[0].data) == size:
        return

    if len(stream[0]) > size:
        stream[0].data = stream[0].data[:size]
    # else: throw exception?

def sample(stream):
    """
    Gets samples list from trace
    :param stream:
    :return:
    """
    # Normalize (by maximum amplitude)
    stream.normalize()
    normalized_data = stream.data

    # Check df and resample if necessary
    resampled_data = []
    if int(stream.trace.stats.sampling_rate) == config.required_df:
        resampled_data = normalized_data
    resampled_data = normalized_data

    # Check length
    result_data = []

    i = 0
    while i < config.required_sample_length:
        if i < len(resampled_data):
            result_data.append(resampled_data[i])
        else:
            # Log message about adding zeroes to result data
            result_data.append(0)

    return result_data
