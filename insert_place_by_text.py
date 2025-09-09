#!/usr/bin/env python3
#
# This is a small script intendet to aid in data maintenance of the endof10-website.
# As of 2025-08-15, it will sort the events by date and print the result.
# Any questions should be sent to aaronwey on matrix or aaronwey@posteo.de, I will gladly help out.
#

import json
import sys
from datetime import datetime
import os
import utils
import json
from pathlib import Path
import os


if __name__ == "__main__":
    basic_path = "/home/aaron/Code/endof10-org/data/events.json"

    initial_data_as_lines = utils.load_from_file_as_lines(basic_path)
    new_data_as_lines = utils.load_from_file_as_lines("./new_data.json")
    base_file_dir = "./emails/"

    all_paths = [
        Path(os.path.join(dp, f))
        for dp, dn, filenames in os.walk(base_file_dir)
        for f in filenames
    ]
    paths_that_jsons = sorted([el for el in all_paths if el.suffix == ".json"])
    events_from_list = []
    list_of_files_as_list = []
    for path_el in paths_that_jsons:
        with open(path_el, "r") as file:
            lines_in_file = [el for el in file.readlines() if el.strip().strip("\n")]
            try:
                result = json.loads("".join(lines_in_file))
            except json.decoder.JSONDecodeError as e:
                print(e)
                print(f"Invalid json in file:{path_el}")
                continue
            list_of_files_as_list.append(lines_in_file)

    list_of_files_as_list = [el for el in list_of_files_as_list if el]
    list_of_files_as_list_that_are_places = [
        el for el in list_of_files_as_list if utils.is_place(el)
    ]

    combined_lines = initial_data_as_lines
    elements_skipped = 0
    elements_added = 0
    segments = utils.split_linelist_into_segments(initial_data_as_lines)
    set_of_existing_events = {
        utils.cast_to_tuple_for_set_cmp_events(el)
        for el in utils.split_linelist_into_segments(initial_data_as_lines)
    }
    # print(initial_data_as_lines, segments, set_of_existing_events)
    print(f"There are currently {len(set_of_existing_events)} events present!")
    # exit()
    for list_el in list_of_files_as_list_that_are_places:
        if utils.cast_to_tuple_for_set_cmp_events(list_el) in set_of_existing_events:
            print("Event likely already added, skipping!")
            elements_skipped = elements_skipped + 1
            continue

        combined_lines = utils.insert_event_into_lines(combined_lines, list_el)
        set_of_existing_events.add(utils.cast_to_tuple_for_set_cmp_events(list_el))
        print(
            f"Added event, there are currently {len(set_of_existing_events)} events present."
        )
        elements_added = elements_added + 1

    print(f"Added: {elements_added}, Skipped: {elements_skipped}")
    print(combined_lines[0:5])
    basic_out_path = "./result.json"
    target = basic_out_path

    if "--in-place" in sys.argv:
        target = basic_path
    try:
        os.remove(target)
    except FileNotFoundError:
        pass
    with open(target, "w") as file:
        file.write("".join(combined_lines))
    print(f"Data has been written to {target}")
