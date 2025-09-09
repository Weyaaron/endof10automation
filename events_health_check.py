#!/usr/bin/env python3
#
# This is a small script intendet to aid in data maintenance of the endof10-website.
# As of 2025-08-15, it will load the events, check for 'obvious' defects and report them.
# Any questions should be sent to aaronwey on matrix or aaronwey@posteo.de, I will gladly help out.
#

import sys
from datetime import datetime
import utils

import urllib.request
from urllib.parse import urlparse


def check_url_is_valid(entry, verbose):
    url = entry.get("url", "")
    try:
        urlparse(url)
    except Exception as e:
        return False, f"{e}"
    return True, ""


def check_url_ping(entry, verbose):
    url = entry.get("url", "")
    try:
        response = urllib.request.urlopen(url, timeout=1)
        if response.getcode() == 200:
            return True, ""
    except Exception as e:
        return False, f"{e}"
    return True, ""


def check_is_complete(entry, verbose):
    expected_keys = [
        "addressCountry",
        "addressCountrylatitude",
        "addressLocality",
        "addressRegion",
        "description",
        "email",
        "endDate",
        "estimatedCost",
        "eventAttendanceMode",
        "extendedAddress",
        "inLanguage",
        "latitude",
        "longitude",
        "name",
        "postalCode",
        "startDate",
        "streetAddress",
        "telephone",
        "url",
    ]

    set_of_actual_keys = set(entry.keys())
    diff = set_of_actual_keys.difference(set(expected_keys))
    if diff:
        print(diff)
    return True, ""


if __name__ == "__main__":
    if "--help" in sys.argv:
        print("This is the manual for the 'check_health' script.")
        print(
            "It will read the events from 'data/events.json', do a number of checks on them and report results."
        )
        print(
            "If you use the argument '--verbose', it will report more details about the issues."
        )
        print(
            "If you use the argument '--exhaustive', it will do more checks which might take a while."
        )
        exit()
    basic_path = "/home/aaron/Code/endof10-org/data/events.json"

    data = utils.load_from_file(basic_path)

    print(f"This healthcheck will check a total of {len(data)} items")
    verbose = "--verbose" in sys.argv

    list_of_check_functions = [check_url_is_valid, check_is_complete]
    if "--exhaustive" in sys.argv:
        list_of_check_functions.append(check_url_ping)

    result_dict = {}

    now = datetime.now().isoformat()

    data_in_future = [el for el in data if el["startDate"] > now]
    print(len(data_in_future))
    for entry_el in data_in_future:
        current_results = []
        for checks in list_of_check_functions:
            result, error = checks(entry=entry_el, verbose=verbose)
            print(result, error)
            current_results.append((result, error))

        errors = [el for el in current_results if el[0] is False]
        result_dict.update({entry_el["name"]: current_results})
        # print(f"The current element had {len(errors)} errors")
    total_errors = 0
    for name, results in result_dict.items():
        errors = [el for el in results if el[0] is False]
        total_errors = total_errors + len(errors)
        if len(errors) > 0:
            print(f"{name} had len(errors) in total")

    print(f"Check completed, {total_errors} found")
