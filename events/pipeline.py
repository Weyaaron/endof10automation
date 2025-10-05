import sys

sys.path.append(".")

from utils.utils import (
    init_git_repo_at_path,
    create_mr,
    input_events,
    prepare_path_for_git_repo,
    validate_events,
    init_branch_name,
    switch_branch,
    insert_event_into_file,
    format_data,
    remove_dir_pending_confirmation,
)

if __name__ == "__main__":
    if "--help" in sys.argv:
        print("This script is intendet to automate work for the campaign 'endof10'.")
        print(
            "It parses events from a file/a directory and opens one PR by event on the git repo provided in the config."
        )

    new_events = input_events()
    valid_events = validate_events(new_events)

    for event_el in valid_events:
        current_git_dir = prepare_path_for_git_repo(event_el)
        new_branch = init_branch_name(event_el)

        event_as_formated_str = format_data(event_el, sorted_keys=True)
        print(f"This event has been parsed succesfully:{event_as_formated_str}")
        user_input_confirmation = input("Please confirm its inclusion with y:")
        if not user_input_confirmation == "y":
            print("Current Event has been skipped!")
            remove_dir_pending_confirmation(current_git_dir)
            continue
        init_git_repo_at_path(current_git_dir)
        # Todo: Implement this
        # events_already_in_place = load_from_file(
        #     determine_file_target_path(current_git_dir)
        # )
        # Todo: Implement this
        # set_of_tuples_of_events_already_in_place = (

        insert_event_into_file(current_git_dir, event_el)
        switch_branch(current_git_dir, new_branch)
        create_mr(current_git_dir, new_branch, event_el)
