from pandas import DataFrame
from sys import argv
import os


def get_keys_lines(file_name):
    list_of_lines = None
    with open(file_name, "r") as txt_file:
        list_of_lines = txt_file.readlines()
        
    keys = list_of_lines[0].strip().split(",")
    tag_lines = list_of_lines[1:]
    return keys, tag_lines


def mend_broken_str(fragments):
    ret_str = ""
    for fragment in fragments:
        ret_str += fragment.strip() + ", "

    return ret_str[:len(ret_str) - 2]


def read_lines_to_dict(keys, lines):
    ret_dict = {}
    for key in keys:
        ret_dict[key] = []
        
    for a in range(len(lines)):
        values = lines[a].strip().split(",")
        if len(values) <= 1:  # Blank line was found
            continue
        
        for b in range(len(values)):
            if b >= len(keys) - 1:
                append_value = mend_broken_str(values[b:])
                ret_dict[keys[b]].append(append_value)
                break

            else:
                ret_dict[keys[b]].append(values[b])
            
    return ret_dict


def dict_to_csv(keys, data_dict, file_name):
    print(f"data_dict: {data_dict}")
    new_frame = DataFrame(data=data_dict)
    print(f"new dataframe: {new_frame}")
    try:
        print(f"Writing to file: {file_name}")
        with open(file_name, mode="w+") as file:
            new_frame.to_csv(path_or_buf=file, columns=keys, index=False)

    except PermissionError as err:
        print("Failed to convert txt to csv, see console for more information")
        print(err)


if __name__ == "__main__":
    try:
        file_name = argv[1]
    except IndexError:
        file_name = input("Please give a txt file name (including extension) to read to a csv:\n")

    sub_dirs = __file__.split("\\")
    curr_dir = ""
    for dir_ind in range(len(sub_dirs) - 1):
        curr_dir += sub_dirs[dir_ind] + "\\"

    file_name = curr_dir + file_name
    
    keys, lines = get_keys_lines(file_name)
    data_dict = read_lines_to_dict(keys, lines)
    dict_to_csv(keys, data_dict, file_name.split(".")[0] + ".csv")
    
    
    