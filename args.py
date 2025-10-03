# This file contain all the args needet for a run.
# They will be loaded from the env or by "input".

import os
import sys


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


GITLAB_TOKEN = get_arg("gitlab_token", "Acces-Token of gitlab")
GITLAB_SSH_URL = get_arg(
    "gitlab_ssh_url", "Full url to the repo intended as a base.('Source of the data')"
)

GITLAB_REPO_ID_TARGET = get_arg(
    "gitlab_repo_id_target",
    "Numeric id of the repo intended as the target of the mr.",
)
GITLAB_SSH_URL = "git@invent.kde.org:aaronwey/endof10-org.git"
REPO_BASE_DIR = "/tmp/"
GITLAB_ROOT = "invent.kde.org"
