import os
import shutil

from datetime import datetime
from typing import Optional
import configparser
import json
import pyperclip
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
import sys

from pathlib import Path


def load_from_file(path_as_str):
    with open(path_as_str, "r") as file:
        content = file.read()

    return json.loads(content)


def format_data(data_as_dict):
    return json.dumps(data_as_dict, indent=2, ensure_ascii=False)


def execute_shell_in_dir(dir: Path, cmd: str):
    full_cmd = f"cd {dir};{cmd}"
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
    # print(stdout, x)


def prepare_path_for_git_repo(event_as_dict: dict) -> Path:
    git_repo_base_dir = load_config_value("local", "base_dir")

    basic_name = event_as_dict.get("name")
    cleaned_name = basic_name.replace("/", "-").replace(" ", "_")

    name_as_path = Path(f"./{cleaned_name}")
    git_dir = Path(git_repo_base_dir).joinpath(name_as_path)
    return git_dir


def cast_into_tuple_for_comparison(event_as_dict: dict) -> tuple:
    return (
        event_as_dict.get("name"),
        event_as_dict.get("startDate"),
        event_as_dict.get("endDate"),
    )


def init_branch_name(event_as_dict: dict) -> str:
    # random_branch_name = f"branch-{random.randrange(0, 100)}"
    # return random_branch_name

    basic_name = event_as_dict.get("name")
    cleaned_name = basic_name.replace("/", "-").replace(" ", "_")

    name_with_date = f"{cleaned_name}-{datetime.today().isoformat()}"
    # Apparently a git branch name does not allow ':'
    return name_with_date.replace(":", "-")


def switch_branch(git_dir: Path, branch_name: str):
    new_branch = f"cd {git_dir};git branch {branch_name}"
    switch_branch = f"cd {git_dir};git switch {branch_name}"
    for command_el in [new_branch, switch_branch]:
        execute_shell_in_dir(git_dir, command_el)


def init_git_repo_at_path(git_dir: Path):
    gitlab_ssh_url = load_config_value("gitlab", "ssh_url")
    # Todo: ask for confirmation
    print(
        f"Attempting to clone into {git_dir}, this might exist, in this case removal will be attempted"
    )
    remove_dir_pending_confirmation(git_dir)
    clone = f"git clone {gitlab_ssh_url} {git_dir}"
    execute_shell_in_dir(Path("~"), clone)


def create_mr(git_dir: Path, local_branch: str, event_as_dict: dict):
    commit_msg = f"add {event_as_dict.get('name')}"
    execute_shell_in_dir(git_dir, "git add .")
    execute_shell_in_dir(git_dir, f"git commit -m'{commit_msg}'")
    execute_shell_in_dir(git_dir, "git push")

    gitlab_token = load_config_value("gitlab", "token")

    gitlab_mr_repo_id = load_config_value("gitlab", "mr_repo_id")
    gitlab_root = load_config_value("gitlab", "root")

    mr_url = f"https://{gitlab_root}/api/v4/projects/{gitlab_mr_repo_id}/merge_requests"
    mr_data = {
        "source_branch": local_branch,
        "target_branch": "master",
        "title": f"Automatic Mr from Pipeline to add event {event_as_dict.get('name')}",
        "description": f"Automated Event update from pipeline containing event {event_as_dict.get('name')}",
        "remove_source_branch": True,
        "squash": True,
        "target_project_id": gitlab_mr_repo_id,
    }

    mr_headers = {"PRIVATE-TOKEN": gitlab_token}
    response = requests.post(mr_url, headers=mr_headers, data=mr_data)
    if response.ok:
        print("✅ Merge request created:", response.json()["web_url"])
    else:
        print("❌ Failed to create merge request:", response.text)


def load_config_file_path() -> Path:
    config_path = ""
    if "--config" not in sys.argv:
        print(
            "You did not provide a config. This is necessary for the programm to run. Plase provide one with --config [path]. The recommended path is 'local.config' The program will exit."
        )
        exit()
    else:
        for i in range(0, len(sys.argv)):
            if sys.argv[i] == "--config":
                config_path = sys.argv[i + 1]

    return Path(config_path).absolute()


def load_config_value(section: str, name: str) -> str:
    config_path = load_config_file_path()
    config = configparser.ConfigParser()

    config.read(config_path)
    try:
        return config.get(section, name)
    except configparser.NoOptionError:
        print(
            f"Your provided config at {config_path} did not provide the value '{name}' in section '{section}'. This argument is mandatory, please edit your config accordingly."
        )
        exit()

    except configparser.NoSectionError:
        print(
            f"Your provided config at {config_path} did not provide the section '{section}'. This section is mandatory, please edit your config accordingly."
        )
        exit()


def validate_config():
    pass


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


def _event_from_str(input_as_str: str) -> Optional[dict]:
    import json

    try:
        return json.loads(input_as_str)
    except json.JSONDecodeError as e:
        print(
            f"Tried to parse the str '{input_as_str}' into json, but it failed with error: '{e}'"
        )
        return {}


def _ensure_is_list(input_data) -> list:
    if isinstance(input_data, list):
        return input_data
    return [input_data]


def attempt_clipboard_parsing() -> dict:
    current_clipboard_text = pyperclip.paste()
    event_from_clipboard = _event_from_str(current_clipboard_text)
    if event_from_clipboard:
        print("The clipboard contained valid json, will continue with this.")
        return _ensure_is_list(event_from_clipboard)
    else:
        print("The clipboard did not contain valid json, will try other options.")


def glob_dir_for_json(base_path: Path) -> list:
    return [el for el in base_path.iterdir() if "json" in el.name]


def input_events() -> list:
    path_for_events = Path(load_config_value("local", "new_event_dir")).absolute()

    all_events = []
    for file_path_el in glob_dir_for_json(path_for_events):
        with open(file_path_el, "r") as file:
            event_str = file.read()
            event_as_dict = _event_from_str(event_str)

            if not event_as_dict:
                print(
                    f"Unable to parse the file {file_path_el}. Please check the input."
                )

            all_events.extend(_ensure_is_list(event_as_dict))

    return all_events

    # event_str = ""
    # if not event_file:
    #     # event_from_clipboard = attempt_clipboard_parsing()
    #     event_from_input = input(
    #         "Please enter a path to a file containing events. You may skip this using 's' to enter json in the next step."
    #     )
    #     if event_from_input == "s":
    #         event_str = input("Please enter a event as a string:")
    # full_path = ""
    # if event_file and not event_str:
    #     full_path = Path(event_file).absolute()


def event_is_valid(event_as_dict: dict) -> bool:
    keys = [
        "name",
        "description",
        "url",
        "streetAddress",
        "postalCode",
        "addressLocality",
        "addressRegion",
        "addressCountry",
        "latitude",
        "longitude",
        "email",
        "estimatedCost",
    ]
    all_keys_exist = True
    for key_el in keys:
        exists = key_el in event_as_dict.keys()
        all_keys_exist = all_keys_exist and exists
        if not exists:
            print(
                f"{event_as_dict['name']} is missing key {key_el} and will be skipped."
            )
    return all_keys_exist


def validate_events(events: list):
    for event_el in events:
        if event_is_valid(event_el):
            print("Succesfully parsed a valid event")
        else:
            print(f"{event_el} is not considered valid and will be skipped")

    # return [el for el in events if event_is_valid(el)]
    return events


def format_data(data_as_dict, sorted_keys=False):
    return json.dumps(data_as_dict, indent=2, ensure_ascii=False, sort_keys=sorted_keys)


def sort_events(events: list) -> list:
    return sorted(events, key=lambda x: datetime.fromisoformat(x.get("startDate")))


def determine_file_target_path(repo_dir: Path) -> Path:
    return repo_dir.joinpath(Path("./data/events.json")).absolute()


def insert_event_into_file(repo_dir: Path, event_as_dict: dict):
    full_path = determine_file_target_path(repo_dir)
    events_from_file = load_from_file(full_path)

    full_events = events_from_file + [event_as_dict]

    sorted_events = sort_events(full_events)

    with open(full_path, "w") as file:
        file.write(format_data(sorted_events))


def remove_dir_pending_confirmation(dir_path: Path):
    if not dir_path.exists():
        return
    user_input_confirmation = input(
        f"Please confirm the deletion of directory {dir_path} and all its children with y:"
    )
    if user_input_confirmation == "y":
        try:
            shutil.rmtree(dir_path)
        except FileNotFoundError:
            pass

    print(f"The directory {dir_path} has been removed.")
