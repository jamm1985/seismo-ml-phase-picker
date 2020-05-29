import os
import sys
import re


def get_files(path, min_depth=0, max_depth=0, exp=r'', max=-1):
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
    all_files = os.walk(path)
    result_files = []

    total = 0
    total_2 = 0
    for x in all_files:
        total += 1
        for file in x[2]:
            total_2 += 1
            if max != -1 and len(result_files) >= max:
                return result_files

            reg_result = re.search(exp, file)
            if reg_result is None:
                continue

            result_files.append(x[0] + '/' + file)

    return result_files
