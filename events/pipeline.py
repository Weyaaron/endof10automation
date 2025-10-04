import sys

sys.path.append(".")
import shutil

SYS_ARG_HELP = "--help"
SYS_ARG_COMMIT = "--commit"
SYS_ARG_IS_IN_COMMIT_MODE = SYS_ARG_COMMIT in sys.argv
SYS_ARG_IS_IN_HELP_MODE = SYS_ARG_HELP in sys.argv
from utils.utils import (
    init_git_repo_at_path,
    create_mr,
    input_events,
    prepare_path_for_git_repo,
    validate_events,
    init_branch_name,
    switch_branch,
    insert_event_into_file,
    load_from_file,
    determine_file_target_path,
    format_data,
)

if __name__ == "__main__":
    if SYS_ARG_IS_IN_HELP_MODE:
        print("This is the manual for this script.")
        print("This script is intendet to automate work for the campaign 'endof10'.")
        print("It is currently work in progress.")
        print(
            "By default, it does not do anything but attempts to parse the events that will be added."
        )
        print("To enable actuall results, please use --commit as an arg.")
        exit()

    if SYS_ARG_IS_IN_HELP_MODE and SYS_ARG_IS_IN_COMMIT_MODE:
        print("Using both help and commit is undefined. Please use just one of these.")
        exit()
    if SYS_ARG_IS_IN_COMMIT_MODE:
        print(
            "This script will do its actions, which might have side effects. Use with caution!"
        )
    else:
        print(
            f"Currently running in dry-mode, which will do the setup but not effect anything. To enable effects, use {SYS_ARG_COMMIT}"
        )

    new_events = input_events()
    valid_events = validate_events(new_events)

    for event_el in valid_events:
        current_git_dir = prepare_path_for_git_repo(event_el)
        new_branch = init_branch_name(event_el)

        init_git_repo_at_path(current_git_dir)

        events_already_in_place = load_from_file(
            determine_file_target_path(current_git_dir)
        )
        # Todo: Implement this
        # set_of_tuples_of_events_already_in_place = (

        event_as_formated_str = format_data(event_el, sorted_keys=True)
        print(f"This event has been parsed succesfully:{event_as_formated_str}")
        user_input_confirmation = input(
            "Please confirm its inclusion with y, any other input will skip this event:"
        )
        if not user_input_confirmation == "y":
            print("Current Event has been skipped!")
            shutil.rmtree(current_git_dir)
            continue
        insert_event_into_file(current_git_dir, event_el)
        switch_branch(current_git_dir, new_branch)
        create_mr(current_git_dir, new_branch, event_el)
