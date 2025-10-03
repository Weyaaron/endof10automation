import sys

if __name__ == "__main__":
    if "--help" in sys.argv:
        print("This is the manual for this script.")
        print("This script is intendet to automate work for the campaign 'endof10'.")
        print("It is currently work in progress")
        print("By default, it does not do anything but runs through some setup.")
        print("To enable actuall results, please use --commit as an arg.")
        exit()

    if "--commit" in sys.argv:
        print(
            "This script will do its actions, which might have side effects. Use with caution!"
        )
    else:
        print(
            "Currently running in dry-mode, which will do the setup but not effect anything. To enable effects, use '--commit'"
        )

    from utils import init_git_repo, create_mr

    local_git_repo_path, local_branch = init_git_repo()
    create_mr(local_git_repo_path, local_branch)
