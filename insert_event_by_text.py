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
            list_of_files_as_list.append(lines_in_file)

    list_of_files_as_list = [el for el in list_of_files_as_list if el]

    combined_lines = initial_data_as_lines
    elements_skipped = 0
    elements_added = 0

    set_of_existing_events = {}
    for list_el in [el for el in list_of_files_as_list if utils.is_event(el)]:
        prior_lines = combined_lines.copy()
        combined_lines = utils.insert_event_into_lines(combined_lines, list_el)
        if prior_lines == combined_lines:
            elements_skipped = elements_skipped + 1
        else:
            elements_added = elements_added + 1

    print(f"Added: {elements_added}, Skipped: {elements_skipped}")
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
