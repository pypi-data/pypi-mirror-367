import os
from pypamguard.core.filters import Filters, WhitelistFilter
from .load_pamguard_binary_file import load_pamguard_binary_file
from .logger import Verbosity

def load_pamguard_multi_file(data_dir, file_names, item_uid, verbosity: Verbosity = Verbosity.WARNING):
    file_name_dict = {}

    event_data = {}
    event_data_list = []

    # Each file name has one or more UIDs. Better represented by dict.
    for file_name, uid in zip(file_names, item_uid):
        if file_name not in file_name_dict:
            file_name_dict[file_name] = []
        file_name_dict[file_name].append(uid)

    for file_name in file_name_dict:
        filter_obj = Filters({
            "uid_list": file_name_dict[file_name]
        })
        file_data = load_pamguard_binary_file(os.path.join(data_dir, file_name), filters=filter_obj)
        # event_data[file_name] = file_data
        # OR
        event_data_list.append(file_data.data)
        # TODO: PUT FILENAME IN load_pamguard_binary_file()

        # THIS SEEMS LIKE A ROUNDABOUT WAY OF DOING OPTION 1
        # FROM MATLAB CODE.
        # fileName = [fName fEnd];
        # for d = 1:numel(fileData)
        #     fileData(d).binaryFile = fileName;
        # end