import os
import json
from email import message


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
