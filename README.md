# Endof10Automation

This repo provides a series of scripts that automate
adding events/places to the website https://endof10.org/.
Since there is some potential to spam gitlab, please use
with caution. This repo is provided as is.

# Setup
A virtual environment is recommended but not
mandatory. Current dependencies are:
- pyperclip

They can be installed by using "pip [name]".

# How to run
All of the scripts are intendet to be run from
the base directory, e.g.:

```python
 python events/sort.py
```


# Organisation
The directories 'events' and 'places' contain
all of the utilities for events and places
respectivly. They contain, in various stages of completion(!):

- sort: Sorts the data
- check: Checks for completion/validity
- pipeline: Opens a mr to gitlab to add new entries

As of 2025-10-04, their status is:

| Modul | Name | Status |
| ----------- | -------- | ---- |
| Events | Sort | Done |
| Events | Check | x |
| Events | Pipeline| Done |
| Places | Sort | x|
| Places | Check | x |
| Places | Pipeline| x |

# How to provide args in a way that avoids manual input during execution

It is encouraged to setup a variety args to avoid manual input.
This can be done in one of two ways: You can edit 'utils/args.py'
in place. This is easy, but has disadvantages when the package will be
updated.

The other option is to export these values using environment-variables.
When you are prompted for a argument, the name of the environment variable
that is required will be printed.

# Contributions
Contributions are very much welcomed, just open an issue and
I will get in touch.

# [License](/LICENSE)
[GPL](LICENSE)
