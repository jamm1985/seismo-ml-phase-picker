import h5py as h5
import config.vars as config
import random


def analyse_dataset(file, max_length=-1):
    """
    Prints dataset info in stdout
    :param file: hdf5 file
    :param max_length: maximum of items to analyse
    """
    print("File {} dataset info:".format(file.filename))
    keys1 = file.keys()
    print(str(list(file.keys())))

    for key in keys1:
        print("{} set length: {}".format(key, len(file[key])))

    # Calculate picks
    p_picks_count = 0
    s_picks_count = 0
    n_picks_count = 0

    index = 0
    for x in file['Y']:
        if x == config.p_code:
            p_picks_count += 1
        if x == config.s_code:
            s_picks_count += 1
        if x == config.noise_code:
            n_picks_count += 1

        index += 1
        if 0 <= max_length <= index:
            print("Analysing finished at position {}".format(index))
            break

    print("P-picks count: {}".format(p_picks_count),
          "S-picks count: {}".format(s_picks_count),
          "Noise-picks count: {}".format(n_picks_count),
          end="\n")
    print("\n")


def merge(files, save_path):
    """
    Merges two datasets together
    :param save_path: path to write new dataset
    :param file_2_limit: limit amount of picks for merging from set 2, do not limit if negative
    :return:
    """
    print("Merging")

    X = []
    Y = []
    Z = []  # If 0, then element came from the first archive, else - from the second

    progress_bar_length = 20

    for f in files:
        print("Processing {}..".format(f["filename"]))
        file = f["file"]

        length = len(file['X'])

        limit = -1 if "limit" not in f.keys() else f["limit"]
        if 0 > limit or limit > length:
            limit = length

        index = 0
        while index < limit:
            X.append(file['X'][index])
            Y.append(file['Y'][index])
            Z.append(f["index"])
            progress_bar(index, limit, progress_bar_length)
            index += 1

        print("\n\n", end="")

    # Shuffle
    zipped = list(zip(X, Y, Z))
    random.shuffle(zipped)
    X_result, Y_result, Z_result = zip(*zipped)

    # Save dataset
    print("\n\nWriting to {}..".format(save_path))
    file = h5.File(save_path, "w")

    dset1 = file.create_dataset('X', data=X_result)
    dset2 = file.create_dataset('Y', data=Y_result)
    dset3 = file.create_dataset('Z', data=Z_result)

    file.close()
    print("Done!")


def progress_bar(count, total, blocks_total):
    """
    Prints progress bar
    :param count: Steps done
    :param total: Steps total
    :param blocks_total: Length of the bar
    :return:
    """
    steps_per_block = total / blocks_total
    blocks_done = count / steps_per_block

    index = 0
    print("\r[{} out of {}] |".format(count, total), end="")
    while index < blocks_total:
        if index < blocks_done:
            print("#", end="")
        else:
            print("-", end="")
        index += 1

    print("|", end="", flush=True)


# Main function body
if __name__ == "__main__":
    home = "/seismo/seisan/WOR/chernykh/"

    files = [{"filename": home + "dagestan.hdf5", "index": 0},
             {"filename": home + "seisan.hdf5", "index": 1},
             {"filename": home + "scsn_ps_2000_2017_shuf.hdf5", "index": 2, "limit": 103565}]

    result_file_name = home + "dagest_seisan_cali.hdf5"

    # Open and analyse all datasets
    for f in files:
        f["file"] = h5.File(f["filename"], "r")
        limit = -1 if "limit" not in f.keys() else f["limit"]
        analyse_dataset(f["file"], limit)

    # Merge
    merge(files, save_path=result_file_name)
