import os
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
from utils.args import GITLAB_TOKEN, REPO_BASE_DIR, GITLAB_SSH_URL, GITLAB_ROOT, get_arg


def load_from_file(path_as_str):
    with open(path_as_str, "r") as file:
        content = file.read()

    return json.loads(content)


def format_data(data_as_dict):
    return json.dumps(data_as_dict, indent=2, ensure_ascii=False)


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


from pathlib import Path


def prepare_path_for_git_repo() -> Path:
    from utils.args import REPO_BASE_DIR

    random_dir = f"endof10automation-repo-{random.randrange(0, 100)}"
    # Todo: Deal with existing directories
    git_dir = Path(REPO_BASE_DIR + random_dir)
    return git_dir


def init_branch_name() -> str:
    random_branch_name = f"branch-{random.randrange(0, 100)}"
    return random_branch_name


def switch_branch(git_dir: Path, branch_name: str):
    from utils.args import GITLAB_TOKEN, REPO_BASE_DIR, GITLAB_SSH_URL, GITLAB_ROOT

    GITLAB_SSH_URL = GITLAB_SSH_URL or get_arg(
        "gitlab_ssh_url",
        "Full url to the repo intended as a base.('Source of the data')",
    )

    new_branch = f"cd {git_dir};git branch {branch_name}"
    switch_branch = f"cd {git_dir};git switch {branch_name}"
    for command_el in [new_branch, switch_branch]:
        execute_shell_in_dir(git_dir, command_el)


def init_git_repo_at_path(git_dir: Path):
    from utils.args import GITLAB_SSH_URL

    GITLAB_SSH_URL = GITLAB_SSH_URL or get_arg(
        "gitlab_ssh_url",
        "Full url to the repo intended as a base.('Source of the data')",
    )

    clone = f"git clone {GITLAB_SSH_URL} {git_dir}"
    execute_shell_in_dir(Path("~"), clone)


def create_mr(git_dir: Path, local_branch: str):
    from utils.args import (
        GITLAB_TOKEN,
        REPO_BASE_DIR,
        GITLAB_SSH_URL,
        GITLAB_ROOT,
        GITLAB_REPO_ID_TARGET,
    )

    execute_shell_in_dir(git_dir, "git add .")
    execute_shell_in_dir(git_dir, "git commit -m'message to be determined'")
    # execute_shell_in_dir(git_dir, "git push")

    GITLAB_TOKEN = GITLAB_TOKEN or get_arg("gitlab_token", "Access-Token for gitlab")

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
        "target_project_id": GITLAB_REPO_ID_TARGET,
    }

    mr_headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
    # response = requests.post(mr_url, headers=mr_headers, data=mr_data)
    # if response.ok:
    #     print("✅ Merge request created:", response.json()["web_url"])
    # else:
    #     print("❌ Failed to create merge request:", response.text)
    #     exit(1)
    # return


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


from typing import Optional


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


def input_events() -> list:
    current_clipboard_text = pyperclip.paste()
    event_from_clipboard = _event_from_str(current_clipboard_text)
    if event_from_clipboard:
        print("The clipboard contained valid json, will continue with this.")
        return _ensure_is_list(event_from_clipboard)
    else:
        print("The clipboard did not contain valid json, will try other options.")

    from utils.args import (
        EVENT_SOURCE_FILE_PATH,
    )

    EVENT_SOURCE_FILE_PATH = EVENT_SOURCE_FILE_PATH or get_arg(
        "event_source_file_path", "A path to a file containing events"
    )
    event_str = ""

    if not EVENT_SOURCE_FILE_PATH:
        EVENT_SOURCE_FILE_PATH = input(
            "Please enter a path to a file containing events. You may skip this using 's' to enter json in the next step."
        )
        if EVENT_SOURCE_FILE_PATH == "s":
            event_str = input("Please enter a event as a string:")
    full_path = ""
    if EVENT_SOURCE_FILE_PATH and not event_str:
        full_path = Path(EVENT_SOURCE_FILE_PATH).absolute()
        with open(full_path, "r") as file:
            event_str = file.read()

    event_as_dict = _event_from_str(event_str)
    if not event_as_dict:
        print("Unable to parse the provided option. Please check the input")
    return _ensure_is_list(event_as_dict)


# Todo: Fix this
def event_is_valid(event_as_dict: dict) -> bool:
    return "startDate" in event_as_dict.keys()


def validate_events(events: list):
    for event_el in events:
        if event_is_valid(event_el):
            print("Succesfully parsed a valid event")
        else:
            print(f"{event_el} is not considered valid and will be skipped")

    # return [el for el in events if event_is_valid(el)]
    return events


from datetime import datetime


def format_data(data_as_dict):
    return json.dumps(data_as_dict, indent=2, ensure_ascii=False)


def sort_events(events: list) -> list:
    return sorted(events, key=lambda x: datetime.fromisoformat(x.get("startDate")))


def insert_event_into_file(repo_dir: Path, event_as_dict: dict):
    from utils.args import EVENT_FILE_PATH_IN_REPO
    import json

    full_path = repo_dir.joinpath(Path(EVENT_FILE_PATH_IN_REPO)).absolute()

    with open(full_path, "r") as file:
        events_from_file = json.load(file)

    full_events = events_from_file + [event_as_dict]

    sorted_events = sort_events(full_events)

    with open(full_path, "w") as file:
        file.write(format_data(sorted_events))

    print(full_path, events_from_file)
