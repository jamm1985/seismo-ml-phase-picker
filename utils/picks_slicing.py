import os
import sys
import obspy.io.nordic.core as nordic_reader
from obspy.core import read
import logging


def slice_from_reading(reading_path, waveforms_path, slice_duration = 5, output_level=0):
    """
    Reads S-file on reading_path and slice relevant waveforms in waveforms_path
    :param reading_path:   string    path to S-file
    :param waveforms_path: string    path to folder with waveform files
    :param slice_duration: int       duration of the slice in seconds
    :param output_level:   int       0 - min output, 5 - max output, default - 0
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

                    # Read and slice waveform
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
                            trace_slice = trace.slice(pick.time, pick.time + slice_duration)
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
        trace[0].write(save_dir + '/' + trace[1], format=file_format)


#
# Parameters:   path    -
# Returns:
def normalize_path(path):
    """
    Normalizes provided path to: /something/something/something
    :param path:    string    path to normalize
    :return:        string    normalized path
    """
    while path[len(path) - 1] == ' ' or path[len(path) - 1] == '/':
        path = path[:len(path) - 1]
    return path
