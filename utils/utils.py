import os
import sys
import re


def get_files(path, min_depth=0, max_depth=0, exp=r'', max=-1, dir_per_event = True):
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
    total_files = 0
    if dir_per_event:
        dirs = os.listdir(path)

        for directory in dirs:
            files_in_dir = []
            all_files = os.walk(path + directory + '/')
            for x in all_files:
                for file in x[2]:
                    if max != -1 and total_files >= max:
                        break

                    reg_result = re.search(exp, file)
                    if reg_result is None:
                        continue

                    files_in_dir.append(x[0] + file)
                    total_files += 1

            if len(files_in_dir) == 3:
                regex_filter = re.search(r'\.[a-zA-Z]{3}', files_in_dir[0])
                type_of_file = regex_filter.group(0)[1]

                pattern = '\.' + type_of_file + '[a-zA-Z]{2}'
                pattern = re.compile(pattern)
                regex_filter2 = re.search(pattern, files_in_dir[1])
                regex_filter3 = re.search(pattern, files_in_dir[2])

                if regex_filter2 is not None and regex_filter3 is not None:
                    result_files.append(files_in_dir)
            if max != -1 and total_files >= max:
                break

    return result_files
