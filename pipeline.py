import sys
sys.path.append(".")

SYS_ARG_HELP = "--help"
SYS_ARG_COMMIT = "--commit"
SYS_ARG_IS_IN_COMMIT_MODE = SYS_ARG_COMMIT in sys.argv
SYS_ARG_IS_IN_HELP_MODE = SYS_ARG_HELP in sys.argv

if __name__ == "__main__":
    if SYS_ARG_IS_IN_HELP_MODE:
        print("This is the manual for this script.")
        print("This script is intendet to automate work for the campaign 'endof10'.")
        print("It is currently work in progress.")
        print("By default, it does not do anything but runs through some setup.")
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

    from utils import init_git_repo, create_mr

    local_git_repo_path, local_branch = init_git_repo()
    create_mr(local_git_repo_path, local_branch)
