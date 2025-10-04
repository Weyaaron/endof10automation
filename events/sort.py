import sys

sys.path.append(".")

from datetime import datetime
import os

from utils.utils import load_from_file, format_data

if __name__ == "__main__":
    if "--help" in sys.argv:
        print("This is the manual for this script.")
        print(
            "It will read the events from a provided file, sort them by date and print them."
        )
        print(
            "If you use the argument '--in-place', it will replace the providid file with the events sorted by date."
        )
        exit()

    basic_path = input(
        "Please provide the source path of the events. Relative works as well:"
    )

    data = load_from_file(basic_path)

    data_sorted = sorted(data, key=lambda x: datetime.fromisoformat(x.get("startDate")))

    if "--in-place" in sys.argv:
        os.remove(basic_path)
        with open(basic_path, "w") as file:
            file.write(format_data(data_sorted))
        print(f"Data has been written to {basic_path}")
    else:
        print(format_data(data_sorted))
