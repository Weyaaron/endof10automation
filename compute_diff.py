import email
from imaplib import IMAP4_SSL
import utils


base_dir = "/home/aaron/tmp_mails/"
all_events_already_done = utils.load_events_from_file()
import json
import os
from pathlib import Path

all_paths = [
    Path(os.path.join(dp, f))
    for dp, dn, filenames in os.walk(base_dir)
    for f in filenames
    # if os.path.splitext(f)[1] == ".txt"
]
paths_that_jsons = [el for el in all_paths if el.suffix == ".json"]
events_from_list = []
for path_el in paths_that_jsons:
    with open(path_el, "r") as file:
        try:
            result = json.load(file)
        except json.decoder.JSONDecodeError:
            print(path_el)
        events_from_list.append(result)

print(all_paths, paths_that_jsons, all_events_already_done)
