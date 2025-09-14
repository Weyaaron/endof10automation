import os
import json
from email import message
from dateutil import parser


def load_from_file(path_as_str):
    with open(path_as_str, "r") as file:
        content = file.read()

    return json.loads(content)


def load_from_file_as_lines(path_as_str):
    with open(path_as_str, "r") as file:
        content = file.readlines()

    return content


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


def extract_date_from_section(lines):
    try:
        line_with_date = [el for el in lines if "startDate" in el][0]
        date_from_this_section = parser.parse(line_with_date.split('"')[3])
        return date_from_this_section
    except IndexError:
        return None


def format_data(data_as_dict):
    return json.dumps(data_as_dict, indent=2, ensure_ascii=False)


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
    start_end_tuples = [
        (start_indexes[i], end_indexes[i]) for i in range(len(start_indexes))
    ]
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
            continue
        lines_in_between_indexes = initial_data_as_lines[start:end]

        date_of_this_section = extract_date_from_section(lines_in_between_indexes)
        if not date_of_this_section:
            # print(f"Exiting early, no date found in {new_data_as_lines}!")
            print(f"Exiting early, no date found in section {lines_in_between_indexes}")
            exit()
            return initial_data_as_lines
        if date_of_this_section > new_date:
            dividing_index = start
            break

    middle = ["  }\n"] + new_data_as_lines[1:-1] + ["  },\n"]

    return (
        initial_data_as_lines[0:dividing_index]
        + middle
        + initial_data_as_lines[dividing_index:]
    )
