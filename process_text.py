import os


def construct_fnames(epoch_list, chat_name_list, path):
    fnames = []
    for epoch_name in epoch_list.keys():
        for chat_name in chat_name_list:
            fnames.append(
                os.path.join(
                    path, "chat_" + chat_name + "_epoch_" + epoch_name + ".csv"
                )
            )
    return fnames


def check_fnames(fnames):
    # check specified file names exist
    for name in fnames:
        if not os.path.exists(name):
            return False
    return True


# Concatenate a list of files into a single file with specified name on specified path
def concatenate_csv_files(file_paths, output_path):
    """
    Assume all headers are the same
    Add categorial column to distinguish origin, depending on how BERtopic works this may be usefull later
    """
    with open(file_paths[0], "r") as file:
        header = file.readline()
    counter = 0
    with open(output_path, "w") as out_file:
        out_file.write(header.rstrip() + ",FileOrigin\n")
        for file in file_paths:
            print(f"Processing File {counter} / {len(file_paths)}")
            with open(file, "r") as in_file:
                in_file.readline()
                for line in in_file:
                    out_file.write(line.rstrip() + "," + file + "\n")
            counter += 1
