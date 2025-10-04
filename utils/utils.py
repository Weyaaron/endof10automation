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
from utils.args import GITLAB_TOKEN, REPO_BASE_DIR, GITLAB_SSH_URL, GITLAB_ROOT, get_arg


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


def init_git_repo_at_path(git_dir: Path):
    from utils.args import GITLAB_TOKEN, REPO_BASE_DIR, GITLAB_SSH_URL, GITLAB_ROOT

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
    from utils.args import (
        GITLAB_TOKEN,
        REPO_BASE_DIR,
        GITLAB_SSH_URL,
        GITLAB_ROOT,
        GITLAB_REPO_ID_TARGET,
    )

    execute_shell_in_dir(git_dir, "git add .")
    execute_shell_in_dir(git_dir, "git commit -m'message to be determined'")
    execute_shell_in_dir(git_dir, "git push")

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


def input_events() -> list:
    from utils.args import (
        EVENT_SOURCE_FILE_PATH,
    )

    EVENT_SOURCE_FILE_PATH = EVENT_SOURCE_FILE_PATH or get_arg(
        "event_source_file_path", "A path to a file containing events"
    )
    event_str = ""

    if not EVENT_SOURCE_FILE_PATH:
        EVENT_SOURCE_FILE_PATH = input("Please enter a path to a event")
        if EVENT_SOURCE_FILE_PATH == "s":
            event_str = input("Please enter a event as a string")

    print(EVENT_SOURCE_FILE_PATH, event_str)


def validate_events(events: list):
    pass
