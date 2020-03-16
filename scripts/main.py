import os
import obspy.io.nordic.core as nordic_reader
from obspy.core import read

import utils.picks_slicing as picks

# Main function body
if __name__ == "__main__":
    path = '/seismo/seisan/'
    readings_path = path + 'REA/'
    waveforms_path = path + 'WAV/'
    db_name = 'IMGG_'
    full_readings_path = readings_path + db_name
    full_waveforms_path = waveforms_path + db_name
    save_dir = '/home/chernykh/WAV3'

    output_level = 0  # 0 - minimal output, 5 - maximum output

    if output_level >= 2:
        print('Readings path: ' + full_readings_path)

    nordic_dir_data = os.walk(full_readings_path)
    nordic_file_names = []

    # Get all nordic files in REA
    for x in nordic_dir_data:
        for file in x[2]:
            nordic_file_names.append(x[0] + '/' + file)

    # Print all nordic file names
    if output_level >= 5:
        print('All nordic files:\n')
        for x in nordic_file_names:
            print(x)

    # Get and process all files with picks
    events_total = 0
    no_picks_total = 0
    with_picks_total = 0
    corrupted_files_total = 0

    if output_level >= 5:
        print('Reading S-files:\n')

    for file in nordic_file_names:
        slices = picks.slice_from_reading(file, full_waveforms_path, output_level)
        if slices != -1:
            picks.save_traces(slices, save_dir)
