import os
import obspy.io.nordic.core as nordic_reader
from obspy.core import read
import logging
import utils.seisan_reader as seisan
import utils.utils as utils
import utils.picking_stats as stats
import config.vars as config
from obspy.io.mseed import InternalMSEEDError
from obspy.core.utcdatetime import UTCDateTime


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


def get_event_id(reading_path):
    """
    Returns events ids from specified REA file
    :param reading_path: path to REA file
    :return: event ID
    """
    with open(reading_path) as file:
        for line in file:
            line = line.strip()
            if len(line) > 73:
                title = line[0:6]
                if title == "ACTION":
                    id_title = line[56:59]
                    if id_title == "ID:":
                        return line[59:73].strip()
    return ""


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
    picks_line = "STAT SP IPHASW"
    for event in events[0].events:
        index += 1

        f = open(reading_path)
        l = [line.strip() for line in f]

        id = None
        picks_started = False
        picks_amount = len(event.picks)
        picks_read = 0
        picks_distance = []
        if config.seconds_high_precision:
            start_seconds = []
        for line in l:
            if picks_started and picks_read < picks_amount and len(line) >= 74:
                try:
                    dist = float(line[70:74])
                except ValueError as e:
                    dist = None
                picks_distance.append(dist)

                if config.seconds_high_precision:
                    try:
                        seconds = float(line[21:27])
                    except ValueError as e:
                        seconds = None
                    start_seconds.append(seconds)

            if len(line) > 73:
                title = line[0:6]
                if title == "ACTION":
                    id_title = line[56:59]
                    if id_title == "ID:":
                        id_str = line[59:73]
                        id = int(id_str)

            if len(line) > 25:
                if line[0:len(picks_line)] == picks_line:
                    picks_started = True

        # Min magnitude check
        if len(event.magnitudes) > 0:
            if event.magnitudes[0].mag < config.min_magnitude:
                continue

        # Max depth check
        if len(event.origins) > 0:
            if event.origins[0].depth is None:
                continue
            if event.origins[0].depth > config.max_depth:
                continue

        try:
            if len(event.picks) > 0:  # Only for files with picks
                if output_level >= 3:
                    logging.info('File: ' + reading_path + ' Event #' + str(index) + ' Picks: ' + str(len(event.picks)))

                picks_index = -1
                for pick in event.picks:
                    if output_level >= 3:
                        logging.info('\t' + str(pick))

                    picks_index += 1
                    if config.seconds_high_precision:
                        if picks_index < len(start_seconds):
                            start_seconds_pick = start_seconds[picks_index]
                        else:
                            start_seconds_pick = pick.time.second
                            print("OUT OF BOUNDS START SECONDS PICK")
                            print("FILE: " + reading_path)
                            print("PICKS: ")
                            for pick_print in event.picks:
                                print(str(pick_print))
                    else:
                        start_seconds_pick = pick.time.seconds
                    pick_time = UTCDateTime(pick.time.year, pick.time.month, pick.time.day, pick.time.hour,
                                            pick.time.minute, start_seconds_pick)

                    if picks_index < len(picks_distance) and picks_distance[picks_index] is not None:
                        if picks_distance[picks_index] > config.max_dist:
                            continue

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
                            if x[4] <= pick_time:
                                if x[5] is not None and pick_time > x[5]:
                                    continue
                                else:
                                    archive_file_path = seisan.archive_path(x, pick_time.year, pick_time.julday,
                                                                            config.archives_path, output_level)

                                    if os.path.isfile(archive_file_path):
                                        try:
                                            arch_st = read(archive_file_path)
                                        except TypeError as error:
                                            if output_level >= 2:
                                                logging.warning('In ' + archive_file_path + ': ' + str(error))
                                            return -1

                                        # arch_st.normalize(global_max=config.global_max_normalizing)  # remove that
                                        # arch_st.filter("highpass", freq=config.highpass_filter_df)  # remove that
                                        # line later
                                        for trace in arch_st:
                                            pick_start_time = pick_time
                                            if trace.stats.starttime > pick_time or pick_time + slice_duration >= trace.stats.endtime:
                                                logging.info('\t\tArchive ' + archive_file_path +
                                                             ' does not cover required slice interval')
                                                continue

                                            shifted_time = pick_time - config.static_slice_offset
                                            end_time = shifted_time + slice_duration

                                            found_archive = True

                                            trace_slice = trace.slice(shifted_time, end_time)
                                            if output_level >= 3:
                                                logging.info('\t\t' + str(trace_slice))

                                            trace_file = x[0] + str(x[4].year) + str(x[4].julday) + x[1] + x[2] + x[3]
                                            event_id = x[0] + str(x[4].year) + str(x[4].julday) + x[2] + x[3]
                                            slice_name_station_channel = (trace_slice, trace_file, x[0], x[1], event_id,
                                                                          pick.phase_hint, id_str)

                                            # print("ID " + str(id_str))
                                            # if id_str == '20140413140958':
                                            # print(x[0])
                                            # if True:#x[0] == 'NKL':
                                            # trace.integrate()
                                            # trace_slice.integrate()
                                            # trace.normalize()
                                            # trace_slice.normalize()
                                            # print('FOUND ID! NORMALIZED')
                                            # print('ARCHIVE: ' + archive_file_path)
                                            # print('FILE: ' + trace_file)
                                            # print('SLICE: ' + str(trace_slice))
                                            # print('TIME: ' + str(shifted_time) + ' till ' + str(end_time))
                                            # print('TRACE: ' + str(trace))
                                            # print('DATA: ' + str(trace_slice.data))

                                            # trace_slice.filter("highpass", freq=config.highpass_filter_df)
                                            # patho = "/seismo/seisan/WOR/chernykh/plots/part/"
                                            # patho2 = "/seismo/seisan/WOR/chernykh/plots/whole/"

                                            # plt.plot(trace_slice.data)
                                            # plt.ylabel('Amplitude')
                                            # plt.savefig(patho + trace_file)
                                            # plt.figure()

                                            # plt.plot(trace.data)
                                            # plt.ylabel('Amplitude')
                                            # plt.savefig(patho2 + trace_file)
                                            # plt.figure()

                                            if len(trace_slice.data) >= 400:
                                                channel_slices.append(slice_name_station_channel)

                    # Read and slice waveform
                    if found_archive:
                        if len(channel_slices) > 0:
                            slices.append(channel_slices)
                        continue

        except ValueError as error:
            if output_level >= 2:
                logging.warning('In ' + reading_path + ': ' + str(error))
            continue

    return sort_slices(slices)


def parse_s_file(reading_path, picks_size):
    """
    Parses s-file to get additional info which is not avaliable with obspy methods
    :param reading_path: path to S-file
    :param picks_size: amount of picks in S-file
    :return: list of parsed info [event ID, distances, seconds], if config/vars.py seconds_high_precision set as False
                then seconds = None
    """
    # Prepare vars
    id = None
    picks_line = "STAT SP IPHASW"  # Beginning of the picks line
    picks_started = False
    picks_read = 0
    picks_dists = []  # Distances
    if config.seconds_high_precision:
        picks_seconds = []
    else:
        picks_seconds = None

    # Parsing
    with open(reading_path, 'r') as f:
        for line in f:
            line = line.strip()
            # Get distance and seconds
            if picks_started and picks_read < picks_size and len(line) >= 74:
                try:
                    dist = float(line[70:74])
                except ValueError as e:
                    dist = None
                picks_dists.append(dist)

                if config.seconds_high_precision:
                    try:
                        seconds = float(line[21:27])
                    except ValueError as e:
                        seconds = None
                    picks_seconds.append(seconds)

                picks_read += 1

            # Get event ID
            if len(line) > 73:
                title = line[0:6]
                if title == "ACTION":
                    id_title = line[56:59]
                    if id_title == "ID:":
                        id_str = line[59:73]
                        id = str(id_str)

            # Check if picks section started
            if len(line) > 25:
                if line[0:len(picks_line)] == picks_line:
                    picks_started = True

    return [id, picks_dists, picks_seconds]


def get_picks(reading_path, archive_definitions=[]):
    """
    Reads S-file and slices waveforms for event
    :param reading_path: path to S-file
    :param archive_definitions: list of archive definitions
    :return: list of lists of picks per station
    """
    # Parse s-file and error checks
    try:
        events = nordic_reader.read_nordic(reading_path, True)  # Events tuple: (event.Catalog, [waveforms file names]
    except nordic_reader.NordicParsingError as e:
        print("In {}: {}".format(reading_path, e))  # Throw exception?
        return -1
    except ValueError as e:
        print("In {}: {}".format(reading_path, e))  # Throw exception?
        return -1
    except AttributeError as e:
        print("In {}: {}".format(reading_path, e))  # Throw exception?
        return -1
    if len(events[0].events) != 1:
        print("In {}: Events number is {}".format(reading_path, len(events[0].events)))  # Throw exception?
        return -1

    event = events[0].events[0]

    if len(event.picks) == 0:
        print("In {}: No picks!".format(reading_path))  # Throw exception?
        return -1

    # Parse S-file additional info
    parsed_data = parse_s_file(reading_path, len(event.picks))

    #print("Parsed data:", "{}".format(parsed_data), sep='\n')
    event_id = parsed_data[0]
    picks_dists = parsed_data[1]
    picks_seconds = parsed_data[2]

    # Min magnitude check
    magnitude = None
    if len(event.magnitudes) > 0:
        magnitude = event.magnitudes[0].mag
        # if event.magnitudes[0].mag < config.min_magnitude:
            # print("In {}") Throw exception?
            # return -1

    # Max depth check
    depth = None
    if len(event.origins) > 0:
        depth = event.origins[0].depth
        # if event.origins[0].depth is None:
            # print("In {}") Throw exception?
            # return -1
        # if event.origins[0].depth > config.max_depth:
            # print("In {}") Throw exception?
            # return -1
    # else:
        # print("In {}") Throw exception?
        # return -1

    # Picks slicing
    index = -1
    # List of picks: [[station, phase, distance, [archive_definition, archive_path, start, end, [archive trace slices]]]]
    result_list = []
    for pick in event.picks:
        index += 1

        # Get pick time
        if config.seconds_high_precision:
            if index < len(picks_seconds):
                if picks_seconds[index] is not None:
                    pick_sec = picks_seconds[index]
                else:
                    pick_sec = pick.time.second
            else:
                print("In {}: Index for picks is out of range for picks_seconds list!".format(reading_path))  # Throw exception?
                return -1
        else:
            pick_sec = pick.time.second

        time = UTCDateTime(pick.time.year, pick.time.month, pick.time.day, pick.time.hour,
                           pick.time.minute, pick_sec)

        # Check pick distance
        distance = None
        if index < len(picks_dists):
            distance = picks_dists[index]
            # if picks_dists[index] is not None:
                # if picks_dists[index] > config.max_dist:
                    # continue
        # else:
            # print("In {}") Throw exception?
            # return -1

        # Find pick in archives
        station = pick.waveform_id.station_code
        station_archives = seisan.station_archives(archive_definitions, station)

        archives_picks = []  # [archive_definition, archive_path, start, end, [archive trace slices]]
        for x in station_archives:
            # Check if archive exists for current pick
            if x[4] > time:
                continue
            if x[5] is not None and time + config.slice_duration - config.static_slice_offset > x[5]:
                continue

            # Find archive
            archive_path = seisan.archive_path(x, time.year, time.julday, config.archives_path)
            if not os.path.isfile(archive_path):
                continue
            try:
                archive_st = read(archive_path)
            except TypeError as e:
                print("In {}: {}".format(reading_path, e))  # Throw exception?
                return -1

            # Get start and end time for pick
            start_time = time - config.static_slice_offset
            end_time = start_time + config.slice_duration

            shifted_start_time = start_time  # + time_shift
            shifted_end_time = end_time  # + time_shift

            archive_picks_list = []  # [[start_time, end_time, trace_slice]]
            for trace in archive_st:
                if trace.stats.starttime > shifted_start_time or shifted_end_time >= trace.stats.endtime:
                    continue

                trace_slice = trace.slice(shifted_start_time, shifted_end_time)

                archive_picks_list.append([trace_slice.stats.starttime, trace_slice.stats.endtime, trace_slice])

            archives_picks.append([x, archive_path, shifted_start_time, shifted_end_time, time, archive_picks_list])

        result_list.append([station, pick.phase_hint, distance, archives_picks])

    # [event_id, reading_path, magnitude, depth,
    #   [[station, phase, distance,
    #       [[archive_definition, archive_path, start, end, pick_time,
    #                                                                   [[start_time, end_time, archive_trace_slices]]
    #       ]]
    #   ]]
    # ]
    return [event_id, reading_path, magnitude, depth, result_list]


def read_picks(save_dir, phase_hint):
    """
    Reads picks of specified phase
    :param save_dir: Base directory of waveforms database
    :param phase_hint: Specified phase
    :return: ljst of picks
    """
    save_dir = utils.normalize_path(save_dir)
    assert os.path.isdir(save_dir), 'No save directory found: \"{}\"'.format(save_dir)

    # Read picking statistics
    try:
        picking_stats = stats.PickStats()
        picking_stats.read(save_dir + '/' + config.picking_stats_file)
    except FileNotFoundError as e:
        picking_stats = None
        print('No picking statistics file found in path {}'.format(save_dir + '/' + config.picking_stats_file))

    result_list = [picking_stats]
    # Read events
    for dir in os.listdir(save_dir):
        dir_full_path = save_dir + '/' + dir
        if os.path.isfile(dir_full_path):
            continue

        # Get stats
        event_stats = stats.EventStats()
        event_stats.read(dir_full_path + '/' + config.event_stats_file)

        # Magnitude check
        if event_stats.magnitude is not None and event_stats.magnitude < config.min_magnitude:
            continue

        # Depth check
        if event_stats.depth is not None and event_stats.depth > config.max_depth:
            continue

        event_list = [event_stats]
        # Read event pick group
        for subdir in os.listdir(dir_full_path):
            subdir_full_path = dir_full_path + '/' + subdir
            if os.path.isfile(subdir_full_path):
                continue

            # Get stats
            slice_stats = stats.SliceStats()
            slice_stats.read(subdir_full_path + '/' + config.picks_stats_file)

            # Phase hint check
            if slice_stats.phase_hint != phase_hint:
                continue

            pick_list = [slice_stats]
            # Read picks
            for pick_file_name in os.listdir(subdir_full_path):
                # Parse name
                name_split = pick_file_name.split('.')

                if type(name_split) is not list:
                    continue

                if len(name_split) != 5:
                    continue

                spip = name_split[2]
                file_format = name_split[4]

                # Check if its accelerogramm
                if config.ignore_acc and spip in config.acc_codes:
                    continue

                # Check file format
                if type(name_split) is list:
                    if file_format == slice_stats.file_format:
                        pick_list.append(subdir_full_path + '/' + pick_file_name)

            event_list.append(pick_list)
        result_list.append(event_list)
    return result_list


def save_picks(picks, save_dir, file_format="MSEED"):
    """
    Writes an event to a specified save dir
    :param picks:
    :param save_dir:
    :param file_format:
    :return:
    """
    # Create save_dir
    save_dir = utils.normalize_path(save_dir)
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)

    # Retrieve event data
    event_id = picks[0]
    reading_path = picks[1]
    magnitude = picks[2]
    depth = picks[3]
    event_picks = picks[4]

    # If no event ID, quit
    if event_id is None or len(event_id) == 0:
        print("In {}: Event ID is empty, cannot create save dir!".format(reading_path))
        return -1

    # Create event directory
    event_dir = save_dir + '/' + event_id
    if not os.path.isdir(event_dir):
        os.mkdir(event_dir)

    # Write event info
    with open(event_dir + '/' + config.event_stats_file, 'w') as f:
        print("[Event Description]", file=f)
        print("{}={}".format("EventID", event_id), file=f)
        print("{}=\"{}\"".format("SFilePath", reading_path), file=f)
        print("{}={}".format("Magnitude", magnitude), file=f)
        print("{}={}".format("Depth", depth), file=f)

    # Save picks
    for pick in event_picks:
        # Retrieve pick info
        station = pick[0]
        phase_hint = pick[1]
        distance = pick[2]
        phase_picks = pick[3]

        # Create picks directory
        index = 0
        picks_dir = "{event_dir}/{station}.{phase_hint}.{index}".format(event_dir=event_dir,
                                                                        station=station,
                                                                        phase_hint=phase_hint,
                                                                        index=index)
        while os.path.isdir(picks_dir):
            index += 1
            picks_dir = "{event_dir}/{station}.{phase_hint}.{index}".format(event_dir=event_dir,
                                                                            station=station,
                                                                            phase_hint=phase_hint,
                                                                            index=index)
        os.mkdir(picks_dir)

        # Write picks info
        with open(picks_dir + '/' + config.picks_stats_file, 'w') as f:
            print("[Picks Description]", file=f)
            print("{}={}".format("EventID", event_id), file=f)
            print("{}=\"{}\"".format("SFilePath", reading_path), file=f)
            print("{}={}".format("Station", station), file=f)
            print("{}={}".format("PhaseHint", phase_hint), file=f)
            print("{}={}".format("Magnitude", magnitude), file=f)
            print("{}={}".format("Depth", depth), file=f)
            print("{}={}".format("Distance", distance), file=f)
            print("{}=\"{}\"".format("FileFormat", file_format), file=f)

            if len(phase_picks) > 0:
                p_pick = phase_picks[0]
                pick_time = p_pick[4]
                pick_start_time = p_pick[2]
                pick_end_time = p_pick[3]
                print("{name}={day}.{month}.{year}-{hour}:{minute}:{second}".format(name="WavePhaseTime",
                                                                                    day=pick_time.day,
                                                                                    month=pick_time.month,
                                                                                    year=pick_time.year,
                                                                                    hour=pick_time.hour,
                                                                                    minute=pick_time.minute,
                                                                                    second=pick_time.second), file=f)
                print("{name}={day}.{month}.{year}-{hour}:{minute}:{second}".format(name="WaveStartTime",
                                                                                    day=pick_start_time.day,
                                                                                    month=pick_start_time.month,
                                                                                    year=pick_start_time.year,
                                                                                    hour=pick_start_time.hour,
                                                                                    minute=pick_start_time.minute,
                                                                                    second=pick_start_time.second), file=f)
                print("{name}={day}.{month}.{year}-{hour}:{minute}:{second}".format(name="WaveEndTime",
                                                                                    day=pick_end_time.day,
                                                                                    month=pick_end_time.month,
                                                                                    year=pick_end_time.year,
                                                                                    hour=pick_end_time.hour,
                                                                                    minute=pick_end_time.minute,
                                                                                    second=pick_end_time.second), file=f)

        # Save trace slices
        for p_pick in phase_picks:
            archive_def = p_pick[0]
            slices = p_pick[5]
            base_file_name = "{picks_dir}/{location}.{station}.{spip}.{phase}".format(picks_dir=picks_dir,
                                                                                 location=archive_def[2],
                                                                                 station=archive_def[0],
                                                                                 spip=archive_def[1],
                                                                                 phase=phase_hint)
            index = 0
            for sl in slices:
                trace_slice = sl[2]
                if len(slices) == 1:
                    trace_file = "{base_file_name}.{format}".format(base_file_name=base_file_name,
                                                                    format=file_format)
                else:
                    trace_file = "{base_file_name}.{index}.{format}".format(base_file_name=base_file_name,
                                                                            index=index,
                                                                            format=file_format)

                trace_slice.write(trace_file, format=file_format)
                index += 1


def save_traces(traces, save_dir, file_format="MSEED"):
    """
    Saves trace/name tuples list to a file
    :param traces:      [(obspy.core.trace.Trace, string)]    list of slice tuples: (slice, name of waveform file)
    :param save_dir:    string                                save path
    :param file_format: string                                format of same wave file, default - miniSEED "MSEED"
    """
    for event in traces:
        if config.dir_per_event and len(event) > 0:
            base_dir_name = event[0][4]
            if len(event[0]) == 7 and event[0][6] is not None:
                base_dir_name = event[0][6]
            dir_name = base_dir_name
            index = 0
            while os.path.isdir(save_dir + '/' + dir_name):
                dir_name = base_dir_name + str(index)
                index += 1
            os.mkdir(save_dir + '/' + dir_name)
        for x in event:
            try:
                if config.dir_per_event:
                    file_name = x[1] + '.' + x[3] + '.' + x[5]
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
        stat_picks = get_single_picks_stations_data(x)
        if type(stat_picks) == list:
            data.extend(stat_picks)

    return data


def get_single_picks_stations_data(nordic_path):
    """
    Returns all picks for stations with corresponding pick time in format: [(UTC start time, Station name)]
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
    except AttributeError as error:
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
