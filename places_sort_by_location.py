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


from utils import load_from_file, format_data

keys = ["addressCountry", "adressRegion"]


def sort_using_recursion(input_as_list, i) -> list:
    if i > len(keys):
        return input_as_list
    key = keys[i]
    keys_for_slices = list(set([el.get(key) for el in input_as_list]))
    # key,slices = [(key, [el for el in input_as_list if el.get(key) == key)])


if __name__ == "__main__":
    if "--help" in sys.argv:
        print("This is the manual for this script.")
        print(
            "It will read the events from 'data/events.json', sort them by date and print them."
        )
        print(
            "If you use the argument '--in-place', it will replace the 'data/events.json' with the events sorted by date."
        )
        exit()
    basic_path = "/home/aaron/Code/endof10-org/data/places.json"

    data = load_from_file(basic_path)
    missing_entries = []

    def key_func(x) -> tuple:
        keys = ["addressCountry", "addressRegion", "addressLocality", "name"]
        result = []
        for el in keys:
            try:
                result.append(x[el])
            except KeyError:
                result.append("")
                missing_entries.append((x, el))

        return tuple(result)

    data_sorted = sorted(data, key=key_func)

    if "--in-place" in sys.argv:
        os.remove(basic_path)
        with open(basic_path, "w") as file:
            file.write(format_data(data_sorted))
        print(f"Data has been written to {basic_path}")
    else:
        print(format_data(data_sorted))

    for tuple_el in missing_entries:
        print(
            f"The following entry is missing '{tuple_el[1]}'",
            format_data(tuple_el[0]),
            "\n",
        )
