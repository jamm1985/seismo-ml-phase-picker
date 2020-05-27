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


def get_stations(nordic_file_names, output_level=0):
    """
    Get all stations from provided S-files
    :param nordic_file_names:   list    List of nordic file full names
    :param output_level:        int     0 - min output, 5 - max output, default - 0
    :return:
    """
    stations = []
    for file in nordic_file_names:
        new_stations = get_event_stations(file, output_level)

        if new_stations == -1:
            continue

        for x in new_stations:
            if x not in stations:
                stations.append(x)

    return sorted(stations)


def get_event_stations(reading_path, output_level=0):
    """
    Reads S-file and gets all stations from it
    :param reading_path:    string  path to REA database
    :param output_level:    int     0 - min output, 5 - max output, default - 0
    :return: 
    """
    if output_level >= 5:
        logging.info('Reading file: ' + reading_path)

    try:
        events = nordic_reader.read_nordic(reading_path, True)  # Events tuple: (event.Catalog, [waveforms file names])
    except nordic_reader.NordicParsingError as error:
        if output_level >= 2:
            logging.warning('In ' + reading_path + ': ' + str(error))
        return -1
    except ValueError as error:
        if output_level >= 2:
            logging.warning('In ' + reading_path + ': ' + str(error))
        return -1
    except AttributeError as error:
        if output_level >= 2:
            logging.warning('In ' + reading_path + ': ' + str(error))
        return -1

    stations = []
    for event in events[0].events:
        try:
            if len(event.picks) > 0:  # Only files with picks have stations data
                for pick in event.picks:
                    stations.append(pick.waveform_id.station_code)
        except ValueError as error:
            if output_level >= 2:
                logging.warning('In ' + reading_path + ': ' + str(error))
            continue

    return stations


def slice_from_reading(reading_path, waveforms_path, slice_duration=5, archive_definitions=[], output_level=0):
    """
    Reads S-file on reading_path and slice relevant waveforms in waveforms_path
    :param reading_path:        string    path to S-file
    :param waveforms_path:      string    path to folder with waveform files
    :param slice_duration:      int       duration of the slice in seconds
    :param archive_definitions: list      list of archive definition tuples (see utils/seisan_reader.py)
    :param output_level:        int       0 - min output, 5 - max output, default - 0
    :return: -1                                  -    corrupted file
             [(obspy.core.trace.Trace, string)]  -    list of slice tuples: (slice, name of waveform file)
    """
    if output_level >= 5:
        logging.info('Reading file: ' + reading_path)

    try:
        events = nordic_reader.read_nordic(reading_path, True)  # Events tuple: (event.Catalog, [waveforms file names])
    except nordic_reader.NordicParsingError as error:
        if output_level >= 2:
            logging.warning('In ' + reading_path + ': ' + str(error))
        return -1
    except ValueError as error:
        if output_level >= 2:
            logging.warning('In ' + reading_path + ': ' + str(error))
        return -1
    except AttributeError as error:
        if output_level >= 2:
            logging.warning('In ' + reading_path + ': ' + str(error))
        return -1

    index = -1
    slices = []
    for event in events[0].events:
        index += 1

        try:
            if len(event.picks) > 0:  # Only for files with picks
                if output_level >= 3:
                    logging.info('File: ' + reading_path + ' Event #' + str(index) + ' Picks: ' + str(len(event.picks)))

                for pick in event.picks:
                    if output_level >= 3:
                        logging.info('\t' + str(pick))

                    # Check phase
                    if pick.phase_hint != 'S' and pick.phase_hint != 'P':
                        logging.info('\t' + 'Neither P nor S phase. Skipping.')
                        continue

                    if output_level >= 3:
                        logging.info('\t' + 'Slices:')

                    # Checking archives
                    found_archive = False
                    if len(archive_definitions) > 0:
                        station = pick.waveform_id.station_code
                        station_archives = seisan.station_archives(archive_definitions, station)

                        channel_slices = []
                        for x in station_archives:
                            if x[4] <= pick.time:
                                if x[5] is not None and pick.time > x[5]:
                                    continue
                                else:
                                    archive_file_path = seisan.archive_path(x, pick.time.year, pick.time.julday,
                                                                            config.archives_path, output_level)
                                    if os.path.isfile(archive_file_path):
                                        arch_st = read(archive_file_path)
                                        for trace in arch_st:
                                            if trace.stats.starttime > pick.time or pick.time + slice_duration >= trace.stats.endtime:
                                                logging.info('\t\tArchive ' + archive_file_path +
                                                             ' does not cover required slice interval')
                                                continue

                                            found_archive = True
                                            trace_slice = trace.slice(pick.time, pick.time + slice_duration)
                                            if output_level >= 3:
                                                logging.info('\t\t' + str(trace_slice))

                                            trace_file = x[0] + str(x[4].year) + str(x[4].julday) + x[1] + x[2] + x[3]
                                            event_id = x[0] + str(x[4].year) + str(x[4].julday) + x[2] + x[3]
                                            slice_name_station_channel = (trace_slice, trace_file, x[0], x[1], event_id,
                                                                          pick.phase_hint)

                                            channel_slices.append(slice_name_station_channel)

                    # Read and slice waveform
                    if found_archive:
                        slices.append(channel_slices)
                        continue

                    if True:
                        continue  # For now ignore WAV database

                    for name in events[1][index]:
                        # Get WAV path from REA path
                        splits = reading_path.split('/')
                        year = splits[len(splits) - 3]
                        month = splits[len(splits) - 2]

                        # If failed: get WAV path from filename
                        if len(year) != 4 or len(month) != 2:
                            splits = name.split('-')
                            year = splits[0]
                            month = splits[1]
                        wav_path = waveforms_path + '/' + year + '/' + month + '/' + name

                        if not os.path.isfile(wav_path):
                            if output_level >= 2:
                                logging.warning(
                                    'In file: ' + reading_path + ' pick trace file: ' + wav_path + ' does not exist')
                                continue

                        wav_st = read(wav_path)
                        for trace in wav_st:
                            time_shift = random.randrange(1, config.slice_offset)
                            shifted_time = pick.time - time_shift
                            end_time = pick.time + slice_duration
                            trace_slice = trace.slice(shifted_time, end_time)
                            if output_level >= 3:
                                logging.info('\t\t' + str(trace_slice))
                            slice_name_pair = (trace_slice, name)
                            slices.append(slice_name_pair)

        except ValueError as error:
            if output_level >= 2:
                logging.warning('In ' + reading_path + ': ' + str(error))
            continue

    return sort_slices(slices)


def save_traces(traces, save_dir, file_format="MSEED"):
    """
    Saves trace/name tuples list to a file
    :param traces:      [(obspy.core.trace.Trace, string)]    list of slice tuples: (slice, name of waveform file)
    :param save_dir:    string                                save path
    :param file_format: string                                format of same wave file, default - miniSEED "MSEED"
    """
    for event in traces:
        for x in event:
            try:
                if config.dir_per_event:
                    file_name = x[1] + '.' + x[5]
                    dir_name = x[4]
                    index = 0
                    while os.path.isdir(save_dir + '/' + dir_name):
                        dir_name = x[4] + str(index)
                        index += 1
                    os.mkdir(save_dir + '/' + dir_name)

                    index = 0
                    while os.path.isfile(save_dir + '/' + dir_name + '/' + file_name):
                        file_name = x[1] + '.' + x[5] + '.' + str(index)
                        index += 1
                    x[0].write(save_dir + '/' + dir_name + '/' + file_name, format=file_format)
                else:
                    file_name = x[1] + '.' + x[5]
                    index = 0
                    while os.path.isfile(save_dir + '/' + file_name):
                        file_name = x[1] + '.' + x[5] + '.' + str(index)
                        index += 1

                    x[0].write(save_dir + '/' + file_name, format=file_format)
            except InternalMSEEDError:
                logging.warning(str(InternalMSEEDError))
            except OSError:
                logging.warning(str(OSError))


def get_picks_stations_data(path_array):
    data = []
    for x in path_array:
        data.extend(get_single_picks_stations_data(x))

    return data


def get_single_picks_stations_data(nordic_path):
    """
    Returns all picks for stations with corresponding pick time in format: [(UTC start time, UTC end time, Station name)]
    :param nordic_path: string  path to REA database
    :return:
    """
    try:
        events = nordic_reader.read_nordic(nordic_path, True)  # Events tuple: (event.Catalog, [waveforms file names])
    except nordic_reader.NordicParsingError as error:
        if config.output_level >= 2:
            logging.warning('In ' + nordic_path + ': ' + str(error))
        return -1
    except ValueError as error:
        if config.output_level >= 2:
            logging.warning('In ' + nordic_path + ': ' + str(error))
        return -1

    index = -1
    slices = []
    for event in events[0].events:
        index += 1

        try:
            if len(event.picks) > 0:  # Only for files with picks
                for pick in event.picks:
                    slice_station = (pick.time, pick.waveform_id.station_code)
                    slices.append(slice_station)

        except ValueError as error:
            if config.output_level >= 2:
                logging.warning('In ' + nordic_path + ': ' + str(error))
            continue

    return slices


def sort_slices(slices):
    """
    Sorts slices by station and then by channel (but it removes all non-unique station, channel pairs)
    :param slices: slices in format: [[trace, filename, station, channel], ...]
    :return: Sorted slices in the same format: [[trace, filename, station, channel], ...]
    """
    result = []
    for x in slices:
        sorted = []
        semi_sorted = []
        # Sort by stations
        x.sort(key=lambda y: y[2])

        # Sort by channels
        found_channels = []
        current_station = x[0][2]
        for y in x:
            if current_station != y[2]:
                current_station = y[2]
                found_channels = []
            if y[3][-1] in found_channels:
                continue
            if y[3][-1] in config.archive_channels_order:
                found_channels.append(y[3][-1])
                semi_sorted.append(y)

        current_station = ""
        index = 0
        for y in semi_sorted:
            if y[2] != current_station:
                current_station = y[2]
                for channel in config.archive_channels_order:
                    sorting_index = index
                    while sorting_index < len(semi_sorted) and semi_sorted[sorting_index][2] == current_station:
                        if semi_sorted[sorting_index][3][-1] == channel:
                            sorted.append(semi_sorted[sorting_index])
                            break
                        sorting_index += 1
            index += 1

        result.append(sorted)

    return result
