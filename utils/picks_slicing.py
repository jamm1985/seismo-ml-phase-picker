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


def slice_from_reading(reading_path, waveforms_path, slice_duration = 5, archive_definitions = [], output_level=0):
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

                    if output_level >= 3:
                        logging.info('\t' + 'Slices:')

                    # Checking archives
                    found_archive = False
                    if len(archive_definitions) > 0:
                        station = pick.waveform_id.station_code
                        station_archives = seisan.station_archives(archive_definitions, station)

                        for x in station_archives:
                            if x[4] <= pick.time:
                                if x[5] is not None and pick.time > x[5]:
                                    continue
                                else:
                                    archive_file_path = seisan.archive_path(x, x[4].year, x[4].julday, config.archives_path, output_level)
                                    if os.path.isfile(archive_file_path):
                                        found_archive = True
                                        arch_st = read(archive_file_path)
                                        for trace in arch_st:
                                            trace_slice = trace.slice(pick.time, pick.time + slice_duration)
                                            if output_level >= 3:
                                                logging.info('\t\t' + str(trace_slice))

                                            trace_file = x[0] + str(x[4].year) + str(x[4].julday) + x[1] + x[2] + x[3]
                                            slice_name_pair = (trace_slice, trace_file)
                                            slices.append(slice_name_pair)

                    # Read and slice waveform
                    if found_archive:
                        continue

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
                                logging.warning('In file: ' + reading_path + ' pick trace file: ' + wav_path + ' does not exist')
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

    return slices


def save_traces(traces, save_dir, file_format="MSEED"):
    """
    Saves trace/name tuples list to a file
    :param traces:      [(obspy.core.trace.Trace, string)]    list of slice tuples: (slice, name of waveform file)
    :param save_dir:    string                                save path
    :param file_format: string                                format of same wave file, default - miniSEED "MSEED"
    """
    for trace in traces:
        try:
            file_name = trace[1]
            index = 0
            while os.path.isfile(save_dir + '/' + file_name):
                file_name = trace[1] + str(index)
                index += 1
            trace[0].write(save_dir + '/' + file_name, format=file_format)
        except InternalMSEEDError:
            logging.warning(str(InternalMSEEDError))
