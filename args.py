# This file contain all the args needet for a run.
# They will be loaded from the env or by "input".

import os
import sys

GITLAB_TOKEN = ""
# GITLAB_SSH_URL = "git@invent.kde.org:aaronwey/endof10-org.git"
GITLAB_SSH_URL = "git@invent.kde.org:aaronwey/endof10-org.git"
REPO_BASE_DIR = "/tmp/"
GITLAB_ROOT = "invent.kde.org"
GITLAB_REPO_ID_TARGET = "22965"


def get_arg(env_name: str, human_name: str):
    from_env = os.getenv(env_name)
    if from_env:
        return from_env
    if not from_env:
        print(
            f"Unable to read the variable '{env_name}' intended to use as {human_name} from the environment. Will ask for your input next."
        )
        # value = input(f"Please provide a value vor the argument '{human_name}'")
    value = input(f"Please provide a value vor the argument '{human_name}':")
    if not value:
        print(
            "Unable to use the provided value, the empty string is not a valid value. Check the documentation for alternatives on how to set this arg"
        )
        exit()
    return value
