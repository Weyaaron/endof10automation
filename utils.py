import os
import json
from email import message
from dateutil import parser

import os
import pandas as pd
from citric import Client as LS_Client
import json
import base64
import subprocess
import hashlib
import time
import requests
import shutil

import subprocess

import os


import random
from pathlib import Path
from args import GITLAB_TOKEN, REPO_BASE_DIR, GITLAB_SSH_URL, GITLAB_ROOT
from args import get_arg


def execute_shell_in_dir(dir: Path, cmd: str):
    full_cmd = f"cd {dir};{cmd}"
    print(full_cmd)
    shell_instance = subprocess.Popen(
        full_cmd,
        shell=True,
        stdin=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=0,
        text=True,
        universal_newlines=True,
    )

    stdout, x = shell_instance.communicate()
    print(stdout, x)


def init_git_repo():
    from args import GITLAB_TOKEN, REPO_BASE_DIR, GITLAB_SSH_URL, GITLAB_ROOT

    random_dir = f"endof10automation-repo-{random.randrange(0, 100)}"
    # Todo: Deal with existing directories
    git_dir = Path(REPO_BASE_DIR + random_dir)
    # git_ssh_url = "git@github.com:Weyaaron/endof10automation.git"
    random_branch_name = f"branch-{random.randrange(0, 100)}"

    GITLAB_SSH_URL = GITLAB_SSH_URL or get_arg(
        "gitlab_ssh_url",
        "Full url to the repo intended as a base.('Source of the data')",
    )

    clone = f"git clone {GITLAB_SSH_URL} {git_dir}"
    new_branch = f"cd {git_dir};git branch {random_branch_name}"
    switch_branch = f"cd {git_dir};git switch {random_branch_name}"
    execute_shell_in_dir(Path("~"), clone)
    for command_el in [new_branch, switch_branch]:
        execute_shell_in_dir(git_dir, command_el)
    return git_dir, random_branch_name


def create_mr(git_dir: Path, local_branch: str):
    from args import (
        GITLAB_TOKEN,
        REPO_BASE_DIR,
        GITLAB_SSH_URL,
        GITLAB_ROOT,
        GITLAB_REPO_ID_TARGET,
    )

    execute_shell_in_dir(git_dir, "git add .")
    execute_shell_in_dir(git_dir, "git commit -m'message to be determined'")
    execute_shell_in_dir(git_dir, "git push")
    # subprocess.run(["git", "diff", default_branch], check=False)

    # push the commit
    # logger.info("push the commit")
    # subprocess.run(["git", "push", "origin", "HEAD:" + branch], check=True)

    GITLAB_TOKEN = GITLAB_TOKEN or get_arg("gitlab_token", "Acces-Token of gitlab")
    mr_headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
    # Todo: Add support for merge-requests across repos

    GITLAB_REPO_ID_TARGET = GITLAB_REPO_ID_TARGET or get_arg(
        "gitlab_repo_id_target",
        "Numeric id of the repo intended as the target of the mr.",
    )

    mr_url = (
        f"https://{GITLAB_ROOT}/api/v4/projects/{GITLAB_REPO_ID_TARGET}/merge_requests"
    )
    mr_data = {
        "source_branch": local_branch,
        "target_branch": "master",
        "title": "Ein Titel",
        "description": "Automated update from CI pipeline. ",
        "remove_source_branch": True,
        "squash": True,
    }
    # --tod:
    # response = requests.post(mr_url, headers=mr_headers, data=mr_data)
    # if response.ok:
    #     print("✅ Merge request created:", response.json()["web_url"])
    # else:
    #     print("❌ Failed to create merge request:", response.text)
    #     exit(1)
    # return


# # testing getenv
# test_getenv = os.getenv("test_getenv")
# print(test_getenv)

# Available variables:
# limesurvey_url
# limesurvey_username
# limesurvey_password
# limesurvey_survey_id
# gitlab_pat
# gitlab_repo
# git_config_user_email
# git_config_user_name
# CI_PROJECT_PATH #Built-in
# CI_PROJECT_ID #Built-in
# CI_DEFAULT_BRANCH #Built-in

# to be removed later:
from tabulate import tabulate


args = {
    "url": os.getenv("limesurvey_url"),
    "username": os.getenv("limesurvey_username"),
    "password": os.getenv("limesurvey_password"),
    "survey": os.getenv("limesurvey_survey_id"),
}
# set filenames name
places_gitlab_json_file = "data/places.json"
places_lime_json_file = "ci/places_lime.json"


def load_imap_name() -> str:
    user_from_env = os.getenv("imap_user")
    if user_from_env:
        return user_from_env
    # Todo: add actuall fallback
    return "aaronwey@posteo.de"


def load_imap_server() -> str:
    user_from_env = os.getenv("imap_user")
    if user_from_env:
        return user_from_env
    # Todo: add actuall fallback
    return "aaronwey@posteo.de"


def load_imap_password() -> str:
    user_from_env = os.getenv("imap_user")
    if user_from_env:
        return user_from_env
    # Todo: add actuall fallback
    return "aaronwey@posteo.de"


def extract_jsons_from_attachment(msg: message) -> list[dict]:
    result = []
    for part in msg.walk():
        if part.get_content_maintype() == "multipart":
            continue
        if part.get("Content-Disposition") is None:
            continue

        if part.get_filename():
            content = part.get_payload(decode=True)
            try:
                resulting_dict = json.loads(content)
                result.append(resulting_dict)
            except (UnicodeDecodeError, json.decoder.JSONDecodeError):
                print(f"Error on msg {message}")

    return result


def load_events_from_file():
    path = "/home/aaron/Code/endof10-org/data/events.json"
    with open(path, "r") as file:
        result = json.load(file)
    return result


def compare_event_json(first_event, second_evend) -> bool:
    same_lat = first_event.get("latitute") == second_evend.get("latitute")
    same_long = first_event.get("longitute") == second_evend.get("longitute")
    same_email = first_event.get("email") == second_evend.get("email")
    return same_lat and same_long and same_email


def load_from_file(path_as_str):
    with open(path_as_str, "r") as file:
        content = file.read()

    return json.loads(content)


def format_data(data_as_dict):
    return json.dumps(data_as_dict, indent=2, ensure_ascii=False)


def load_from_file_as_lines(path_as_str):
    with open(path_as_str, "r") as file:
        content = file.readlines()

    return content


def compare_event_json(first_event, second_evend) -> bool:
    same_lat = first_event.get("latitute") == second_evend.get("latitute")
    same_long = first_event.get("longitute") == second_evend.get("longitute")
    same_email = first_event.get("email") == second_evend.get("email")
    return same_lat and same_long and same_email


def extract_date_from_section(lines):
    try:
        line_with_date = [el for el in lines if "startDate" in el][0]
        date_from_this_section = parser.parse(line_with_date.split('"')[3])
        return date_from_this_section
    except IndexError:
        return None


def is_event(lines):
    line_with_date = [el for el in lines if "startDate" in el]
    return line_with_date


def is_place(lines):
    opening_hours = [el for el in lines if "openingHours" in el]
    return opening_hours


def extract_value_by_name(lines, key):
    line_with_key = [el for el in lines if key in el][0]
    if line_with_key:
        try:
            return line_with_key.split('"')[3]
        except IndexError:
            print(f"Unable to locate {key} in {line_with_key}")
            return ""
    return ""


def cast_to_tuple_for_set_cmp_events(lines):
    keys = [
        "startDate",
        "endDate",
        "name",
    ]
    result = []
    for el in keys:
        result.append(extract_value_by_name(lines, el))
    return tuple(result)

    # keys = ["startDate", "endDate", "latitude", "longitude"]
    # Todo: Extract lang, long


def construct_start_end_indexes(list_of_lines) -> list:
    start_indexes = [
        i for i in range(len(list_of_lines)) if list_of_lines[i].strip() == "{"
    ]

    end_indexes = [
        i for i in range(len(list_of_lines)) if list_of_lines[i].strip() in ["},", "}"]
    ]
    print(len(start_indexes), len(end_indexes))
    assert len(start_indexes) == len(end_indexes)
    start_end_tuples = [
        (start_indexes[i], end_indexes[i]) for i in range(len(start_indexes))
    ]
    for i in range(len(start_end_tuples) - 1):
        diff = start_end_tuples[i][1] - start_end_tuples[i + 1][0]
        inner_diff = start_end_tuples[i][0] - start_end_tuples[i][1]
        # print(i, start_end_tuples[i], start_end_tuples[i + 1], diff, inner_diff, "\n")
        assert diff == -1

    return start_end_tuples


def split_linelist_into_segments(list_of_lines) -> list:
    segments = []
    for start, end in construct_start_end_indexes(list_of_lines):
        start = min(start, end)
        end = max(start, end)
        if start == end:
            continue
        lines_in_between_indexes = list_of_lines[start:end]
        segments.append(lines_in_between_indexes)
    return segments


def insert_event_into_lines(initial_data_as_lines, new_data_as_lines) -> list:
    new_date = extract_date_from_section(new_data_as_lines)

    dividing_index = 0

    for start, end in construct_start_end_indexes(initial_data_as_lines):
        try:
            assert start < end
        except AssertionError:
            pass
        start = min(start, end)
        end = max(start, end)
        if start == end:
            print(f"Start equals end")
            continue
        lines_in_between_indexes = initial_data_as_lines[start:end]

        date_of_this_section = extract_date_from_section(lines_in_between_indexes)
        if not date_of_this_section:
            # print(f"Exiting early, no date found in {new_data_as_lines}!")
            print(f"Exiting early, no date found in section {lines_in_between_indexes}")
            exit()
            return initial_data_as_lines
        # print(
        #     date_of_this_section, new_date, type(date_of_this_section), type(new_date)
        # )
        if date_of_this_section > new_date:
            dividing_index = start
            print(f"Dividing index found: {dividing_index}")
            break

    middle = ["  },\n", "  {\n"] + new_data_as_lines[1:-1] + ["  },\n"]

    result = (
        initial_data_as_lines[0 : dividing_index - 1]
        + middle
        + initial_data_as_lines[dividing_index:]
    )
    return result


def compare_places_as_lines(first_lines, second_lines):
    pass


def insert_place_into_lines(initial_data_as_lines, new_data_as_lines) -> list:
    new_date = extract_date_from_section(new_data_as_lines)

    dividing_index = 0

    for start, end in construct_start_end_indexes(initial_data_as_lines):
        try:
            assert start < end
        except AssertionError:
            pass
        start = min(start, end)
        end = max(start, end)
        if start == end:
            print(f"Start equals end")
            continue
        lines_in_between_indexes = initial_data_as_lines[start:end]

        date_of_this_section = extract_date_from_section(lines_in_between_indexes)
        if not date_of_this_section:
            # print(f"Exiting early, no date found in {new_data_as_lines}!")
            print(f"Exiting early, no date found in section {lines_in_between_indexes}")
            exit()
            return initial_data_as_lines
        # print(
        #     date_of_this_section, new_date, type(date_of_this_section), type(new_date)
        # )
        if date_of_this_section > new_date:
            dividing_index = start
            print(f"Dividing index found: {dividing_index}")
            break

    middle = ["  },\n", "  {\n"] + new_data_as_lines[1:-1] + ["  },\n"]

    result = (
        initial_data_as_lines[0 : dividing_index - 1]
        + middle
        + initial_data_as_lines[dividing_index:]
    )
    return result


def sort_up_until_month(data):
    pass
    slice_length = 50
    print(len(data))

    sorted_slice = data[0:slice_length]
    unsorted_slice = data[slice_length : len(data)]
    from datetime import datetime
    import pytz

    month = datetime.fromisoformat("2025-06-01").astimezone(pytz.utc)
    print(month)
    previous_slice = [
        el for el in data if datetime.fromisoformat(el.get("startDate")) < month
    ]

    later_slice = [
        el for el in data if datetime.fromisoformat(el.get("startDate")) > month
    ]

    sorted_slice = sorted(
        previous_slice, key=lambda x: datetime.fromisoformat(x.get("startDate"))
    )
    data_sorted = sorted_slice + later_slice
    assert len(data_sorted) == len(data)


def setup_logger():
    import logging
    import traceback

    logger = logging.getLogger(__name__)
    logging.basicConfig(
        format="%(levelname)-8s | %(asctime)s.%(msecs)03d | %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler()],
    )
    # logger.info('Testing Info Message')
    # logger.warning('Warning Message')
    # logger.error('Error Message')
    # logger.critical('Critical Message')
    logger.info("Pipeline started - scheduled pipeline limesurvey places.")

    logger.info("Importing needed libraries.")
    return logger

