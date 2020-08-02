import os
from os.path import isdir
from os.path import isfile
import re
from pathlib import Path

import config.vars as config


def get_files(path, min_depth=0, max_depth=0, exp=r'', max=-1, dir_per_event = True, is_noise = False):
    """
    Returns list of all files in provided path
    Generates exception:
    :param path:      string  - path to directory for file search
    :param min_depth: integer - min depth of files to search, default: 0
    :param max_depth: integer - max depth of files to search, default: 0
    :param exp:       string  - regexp to filter filenames, default: empty
    :return: Returns list of pairs: (full path, relative base) where relative base is part of full path
             except <path> parameter and filename (e.g. <path> = /home/user/, full path = /home/user/dir/dir2/path,
             then relative base = dir/dir2/)
    """
    result_files = []
    total_events = 0
    if dir_per_event:
        dirs = os.listdir(path)

        for directory in dirs:
            if max != -1 and total_events >= max :
                break

            files_in_dir = []
            all_files = os.walk(path + directory + '/')
            for x in all_files:
                for file in x[2]:
                    reg_result = re.search(exp, file)
                    if reg_result is None:
                        continue

                    files_in_dir.append(x[0] + file)

                    if is_noise:
                        id = 0
                    else:
                        p = Path(x[0] + file)
                        parts = p.parts
                        id = 0
                        if len(parts) >= 2:
                            id = int(parts[len(parts) - 2])

            if len(files_in_dir) == 3:
                regex_filter = re.search(r'\.[a-zA-Z]{3}', files_in_dir[0])
                type_of_file = regex_filter.group(0)[1]

                pattern = '\.' + type_of_file + '[a-zA-Z]{2}'
                pattern = re.compile(pattern)
                regex_filter2 = re.search(pattern, files_in_dir[1])
                regex_filter3 = re.search(pattern, files_in_dir[2])

                if regex_filter2 is not None and regex_filter3 is not None:
                    # Sort files_in_dir by channels order
                    ordered_files_id_dir = []
                    for channel in config.order_of_channels:
                        for file in files_in_dir:
                            if file[len(file) - 3] == channel:
                                ordered_files_id_dir.append(file)
                                break

                    ordered_files_id_dir.append(id)

                    if len(ordered_files_id_dir) == 4:
                        result_files.append(ordered_files_id_dir)

                    total_events += 1

    return result_files


def get_nordic_files(readings_path):
    """
    Returns list of full filenames of REA files from given database directory parameter (which can be
            a single path or list of paths
    :param readings_path: string or list of strings - full path to database directory
    :return: list of strings - full filenames of REA files
    """
    nordic_file_names = []
    if type(readings_path) is list:
        for file in readings_path:
            names = get_nordic_files_from_path(file)
            if names is not None:
                nordic_file_names.extend(names)
    else:
        names = get_nordic_files_from_path(readings_path)
        if names is not None:
            nordic_file_names = names

    return nordic_file_names


def get_nordic_files_from_path(readings_path):
    """
    Returns list of full filenames of REA files from given database directory
    :param readings_path: string - full path to database directory
    :return: list of strings - full filenames of REA files
    """
    if type(readings_path) is not str:
        return None

    nordic_dir_data = os.walk(readings_path)
    nordic_file_names = []

    for x in nordic_dir_data:
        for file in x[2]:
            nordic_file_names.append(x[0] + '/' + file)

    return nordic_file_names


def normalize_path(path):
    """
    Normalizes provided path to: /something/something/something
    :param path:    string    path to normalize
    :return:        string    normalized path
    """
    while path[len(path) - 1] == ' ' or path[len(path) - 1] == '/':
        path = path[:len(path) - 1]
    return path


def event_exists(path):
    """
    Checks if specified event exists
    :param path: path to event directory
    :return: True - if event exists, false otherwise
    """
    if not isdir(normalize_path(path)):
        return False

    if not isfile(normalize_path(path) + '/' + config.event_stats_file):
        return False

    # Check event stats file

    return True
