import email
from imaplib import IMAP4_SSL
import utils


base_dir = "/home/aaron/tmp_mails/"

import os
from pathlib import Path

all_paths = [
    Path(os.path.join(dp, f))
    for dp, dn, filenames in os.walk(base_dir)
    for f in filenames
    # if os.path.splitext(f)[1] == ".txt"
]
paths_that_jsons = [el for el in all_paths if el.suffix == ".json"]

print(all_paths, paths_that_jsons)
