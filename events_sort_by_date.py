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


def load_from_file(path_as_str):
    with open(path_as_str, "r") as file:
        content = file.read()

    return json.loads(content)


def format_data(data_as_dict):
    return json.dumps(data_as_dict, indent=2, ensure_ascii=False)


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
    basic_path = "/home/aaron/Code/endof10-org/data/events.json"

    data = load_from_file(basic_path)

    data_sorted = sorted(data, key=lambda x: datetime.fromisoformat(x.get("startDate")))

    if "--in-place" in sys.argv:
        os.remove(basic_path)
        with open(basic_path, "w") as file:
            file.write(format_data(data_sorted))
        print(f"Data has been written to {basic_path}")
    else:
        print(format_data(data_sorted))
