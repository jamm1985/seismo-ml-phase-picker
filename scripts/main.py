import os
import obspy.io.nordic.core as nordic_reader
from obspy.core import read

if __name__ == "__main__":
    path = '/seismo/seisan/'
    readings_path = path + 'REA/'
    waveforms_path = path + 'WAV/'
    db_name = 'IMGG_/2017/04/'  # TO-DO: Change to just IMGG_, update file wav search
    full_readings_path = readings_path + db_name + '/'
    full_waveforms_path = waveforms_path + db_name
    save_dir = '/home/chernykh/WAV'

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
        if output_level >= 5:
            print('Reading file ' + file)

        try:
            events = nordic_reader.read_nordic(file, True)  # Events tuple: (event.Catalog, [waveforms file names])
        except nordic_reader.NordicParsingError as error:
            corrupted_files_total += 1
            if output_level >= 2:
                print('In ' + file + ': ' + str(error))
            continue
        except ValueError as error:
            if output_level >= 2:
                print('In ' + file + ': ' + str(error))
            continue

        events_in_file = 0
        index = -1

        for event in events[0].events:
            index += 1
            try:
                if len(event.picks) > 0:  # Only for files with picks
                    with_picks_total += 1

                    if output_level >= 3:
                        print('File: ' + file + ' Event #' + str(events_in_file) + ' Picks: ' + str(len(event.picks)))

                    for pick in event.picks:
                        if output_level >= 3:
                            print('\t' + str(pick))

                        if output_level >= 3:
                            print('\t' + 'Slices:')

                        # Read and slice waveform
                        for name in events[1][index]:
                            wav_path = full_waveforms_path + name
                            wav_st = read(wav_path)
                            for trace in wav_st:
                                trace_slice = trace.slice(pick.time)

                                if output_level >= 3:
                                    print('\t\t' + str(trace_slice))

                                trace_slice.write(save_dir + '/' + name, format="MSEED")
                                if output_level >= 4:
                                    print('\t\t' + 'slice saved in path: ' + save_dir + '/' + name)
                else:
                    no_picks_total += 1

                events_in_file += 1
                events_total += 1
            except ValueError as error:
                if output_level >= 2:
                    print('In ' + file + ': ' + str(error))
                continue

    if output_level >= 1:
        print('Corrupted files: ' + str(corrupted_files_total))

    if output_level >= 2:
        print('Events total: ' + str(events_total))
        print('Events with picks: ' + str(with_picks_total))
