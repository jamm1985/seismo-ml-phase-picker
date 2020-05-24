import os
import sys

def get_files(path, min_depth = 0, max_depth = 0, exp = ''):
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
    return []
