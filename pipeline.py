# used so far
import os
import pandas as pd
from citric import Client as LS_Client
import json
import base64
import subprocess
import hashlib
import time
import requests
import shutil


# # testing getenv
# test_getenv = os.getenv("test_getenv")
# print(test_getenv)

# Available variables:
# limesurvey_url
# limesurvey_username
# limesurvey_password
# limesurvey_survey_id
# gitlab_pat
# gitlab_repo
# git_config_user_email
# git_config_user_name
# CI_PROJECT_PATH #Built-in
# CI_PROJECT_ID #Built-in
# CI_DEFAULT_BRANCH #Built-in

# to be removed later:
from tabulate import tabulate
from utils import setup_logger, download_limesurvey_raw

logger = setup_logger()
logger.info("Loading configuration.")
args = {
    "url": os.getenv("limesurvey_url"),
    "username": os.getenv("limesurvey_username"),
    "password": os.getenv("limesurvey_password"),
    "survey": os.getenv("limesurvey_survey_id"),
}
args = {"url":}
# set filenames name
places_gitlab_json_file = "data/places.json"
places_lime_json_file = "ci/places_lime.json"

download_limesurvey_raw()
exit()


# function to transform lime survey df into hugo df
def lime_to_hugo_df(df):
    # transform hugo_df into hugo format
    # delete non-needed columns by keeping only needed columns
    # needed_columns = ['Q01[name]', 'Q01[url]', 'Q01[streetAddress]', 'Q01[postalCode]', 'Q01[addressLocality]', \
    #     'Q01[addressRegion]', 'addressCountry', 'addressCountry[other]', 'Q01[latitude]','Q01[longitude]', 'Q01[telephone]', \
    #     'Q01[email]', 'Q01[openingHours]', 'Q01[estimatedCos]', 'Q02', 'Q03[yes]']
    needed_columns = [
        "name",
        "description",
        "url",
        "addressCountry",
        "addressCountry[other]",
        "streetAddress",
        "postalCode",
        "addressLocality",
        "addressRegion",
        "latitude",
        "longitude",
        "telephone",
        "email",
        "openingHours",
        "estimatedCost",
    ]
    # 'lastpage', 'privateContact', 'comments', 'confirm[yes]'

    # rename needed columns
    df = df[needed_columns]
    # df=df.rename(columns={'Q01[name]': 'name', 'Q01[url]': 'url', 'Q01[streetAddress]': 'streetAddress', \
    #     'Q01[postalCode]': 'postalCode', 'Q01[addressLocality]': 'addressLocality', 'Q01[addressRegion]': 'addressRegion', \
    #     'addressCountry': 'addressCountry', 'addressCountry[other]':'addressCountry_other', 'Q01[latitude]': 'latitude','Q01[longitude]': 'longitude', \
    #     'Q01[telephone]': 'telephone', 'Q01[email]': 'email', 'Q01[openingHours]': 'openingHours', \
    #     'Q01[estimatedCos]': 'estimatedCost'
    #     })
    df = df.rename(
        columns={
            "name": "name",
            "description": "description",
            "url": "url",
            "addressCountry": "addressCountry",
            "addressCountry[other]": "addressCountry[other]",
            "streetAddress": "streetAddress",
            "postalCode": "postalCode",
            "addressLocality": "addressLocality",
            "addressRegion": "addressRegion",
            "latitude": "latitude",
            "longitude": "longitude",
            "telephone": "telephone",
            "email": "email",
            "openingHours": "openingHours",
            "estimatedCost": "estimatedCost",
        }
    )
    return df


logger.info("git config")
# Load env
project_path = os.environ["CI_PROJECT_PATH"]  # Built-in
project_id = os.environ["CI_PROJECT_ID"]  # Built-in
default_branch = (
    "pipeline-places-from-limesurvey-to-mr"  # os.environ["CI_DEFAULT_BRANCH"] #Built-in
)
gitlab_pat = os.environ["gitlab_pat"]
gitlab_repo = os.environ["gitlab_repo"]
git_config_user_name = os.environ["git_config_user_name"]
git_config_user_email = os.environ["git_config_user_email"]

# make sure git name and email are set
subprocess.run(["git", "config", "user.name", git_config_user_name], check=True)
subprocess.run(["git", "config", "user.email", git_config_user_email], check=True)

# set remote repo
logger.info("Set remote repo git")
subprocess.run(
    [
        "git",
        "remote",
        "set-url",
        "origin",
        f"https://oauth2:{gitlab_pat}@{gitlab_repo}/{project_path}.git",
    ],
    check=True,
)


# function to write json and send a MR
def mrf(branch, msg, places_df, index):
    # checkout the new branch
    logger.info("Create branch " + branch)
    subprocess.run(["git", "checkout", "-b", branch], check=True)

    # write the make the df into places.json and save file
    logger.info("Writing to file " + places_gitlab_json_file)
    places_df.to_json(
        places_gitlab_json_file, orient="records", indent=2
    )  # , compression='infer')

    # add the file to the commit
    logger.info("adding file to git")
    subprocess.run(["git", "add", places_gitlab_json_file], check=True)

    # commit
    logger.info("Commit git")
    subprocess.run(["git", "commit", "-m", msg], check=False)

    # commit
    logger.info("git diff")
    subprocess.run(["git", "diff", default_branch], check=False)

    # push the commit
    logger.info("push the commit")
    subprocess.run(["git", "push", "origin", "HEAD:" + branch], check=True)

    # send merge request
    mr_headers = {"PRIVATE-TOKEN": gitlab_pat}
    mr_url = f"https://{gitlab_repo}/api/v4/projects/{project_id}/merge_requests"
    mr_data = {
        "source_branch": branch,
        "target_branch": default_branch,
        "title": msg,
        "description": "Automated update from CI pipeline. " + msg,
        "remove_source_branch": True,
        "squash": True,
    }

    response = requests.post(mr_url, headers=mr_headers, data=mr_data)
    if response.ok:
        print("✅ Merge request created:", response.json()["web_url"])
    else:
        print("❌ Failed to create merge request:", response.text)
        exit(1)
    return


# get the data from lime survey in json format using citric


# remove the empty rows
# if lastpage !=1 from the row because it is empty
# remove those who didn't accept the terms (this should be mandatory from the input but still better double check)
logger.info("Cleaning the data from unsubmitted rows.")
lime_new_df = lime_new_df[
    (lime_new_df["lastpage"] == "1") & (lime_new_df["confirm[yes]"] == "Y")
]
# logger.info('Print Tabulate of cleaned new rows from limesurvey data.')
# print(tabulate(new_rows_df, headers='keys', tablefmt='psql'))

# keep needed columns, rename column names
logger.info("Clean Data: Remove non-needed columns and rename the other columns.")
lime_new_df = lime_to_hugo_df(lime_new_df)
# logger.info('Print Tabulate of formatted new rows from limesurvey data.')
# print(tabulate(new_rows_df, headers='keys', tablefmt='psql'))

# New code to read from old lime json file (new format)
logger.info("Getting data from old data into df.")
with open(places_lime_json_file, "r") as file:
    old_data = json.load(file)
lime_old_df = pd.DataFrame.from_dict(pd.json_normalize(old_data), orient="columns")

# # output the dataframe # remove later ###################################################
# logger.info('Print Tabulate of old data from df.')
# print(tabulate(lime_old_df, headers='keys', tablefmt='psql'))
# logger.info('Print Tabulate of limesurvey data from df.')
# print(tabulate(lime_new_df, headers='keys', tablefmt='psql'))


# Compare the previously imported dfs
# - [ ] compare the 2 dfs and identify only new records (based on the id or the seed)
logger.info("Comparing new data to old.")
new_rows_df = pd.concat([lime_old_df, lime_new_df]).drop_duplicates(keep=False)


if new_rows_df.shape[0] > 0:
    # backup the places.json file
    shutil.copy(places_gitlab_json_file, places_gitlab_json_file + ".swp")

    logger.info("Found " + str(new_rows_df.shape[0]) + " records")

    # Open and read the JSON file places.json into df
    logger.info("Getting data from places.json into df.")
    with open(places_gitlab_json_file, "r") as file:
        places = json.load(file)
    places_df = pd.DataFrame.from_dict(pd.json_normalize(places), orient="columns")
    # logger.info('Print Tabulate of formatted places.json df.')
    # print(tabulate(places_df, headers='keys', tablefmt='psql'))

    # TODO ask about extendedAddress?

    # commit and send merge request for the new lime json before committing the otehrs
    # # checkout the default branch in order not to commit places.json
    # logger.info('Checkout default ' + default_branch + ' in order not to commit places.json')
    # subprocess.run(["git", "checkout", "-b", default_branch], check=True)

    # # recover the old version of the places.json and delete the backup
    # shutil.copy(places_gitlab_json_file + ".swp", places_gitlab_json_file)
    # os.remove(places_gitlab_json_file + ".swp")
    # logger.info('Restore places.json')
    # subprocess.run(["git", "restore", places_gitlab_json_file], check=True)

    # update the limesurvey json and commit
    hash = hashlib.sha1()
    hash.update(str(time.time()).encode("utf-8"))
    branch_new_lime_data = "new_lime_data_" + hash.hexdigest()
    # checkout the new branch
    logger.info("Create branch " + branch_new_lime_data)
    subprocess.run(["git", "checkout", "-b", branch_new_lime_data], check=True)

    lime_new_df.to_json(places_lime_json_file, orient="records", indent=2)

    # add the file to the commit
    logger.info("add new lime json places file to git")
    subprocess.run(["git", "add", places_lime_json_file], check=True)

    # commit
    logger.info("Commit new lime json places file to git")
    subprocess.run(
        ["git", "commit", "-m", "Update the places lime json file"], check=False
    )

    # commit
    logger.info("git diff")
    subprocess.run(["git", "diff", default_branch], check=False)

    # push the commit
    logger.info("push the commit")
    subprocess.run(
        ["git", "push", "origin", "HEAD:" + branch_new_lime_data], check=True
    )

    # send merge request for the new lime json file
    mr_headers = {"PRIVATE-TOKEN": gitlab_pat}
    mr_url = f"https://{gitlab_repo}/api/v4/projects/{project_id}/merge_requests"
    mr_data = {
        "source_branch": branch_new_lime_data,
        "target_branch": default_branch,
        "title": "Updating lime json file with new data " + branch_new_lime_data,
        "description": "Automated update from CI pipeline. Updating lime json file with new data "
        + branch_new_lime_data,
        "remove_source_branch": True,
        "squash": True,
    }

    mr_response = requests.post(mr_url, headers=mr_headers, data=mr_data)
    if mr_response.ok:
        print("✅ Merge request created:", mr_response.json()["web_url"])
    else:
        print("❌ Failed to create merge request:", mr_response.text)
        exit(1)

    mr_response.raise_for_status()
    mr = mr_response.json()

    # # Automatically accept the MR
    # amr_url = f"https://{gitlab_repo}/api/v4/projects/{project_id}/merge_requests/{mr['iid']}/merge"
    # amr_data = {
    #     "merge_when_pipeline_succeeds": False,
    #     "should_remove_source_branch": True,
    #     "squash": True
    # }
    # accept_resp = requests.put(amr_url, headers=mr_headers, data=amr_data)
    # # accept_resp.raise_for_status()
    # # logger.info("MR merged successfully.")

    # for each row in new_row_df:
    for index, row in new_rows_df.iterrows():
        logger.info("Adding New Place to places")

        # TODO: add logic here to check required data is inserted (e.g. name should exist)

        # generate the new row
        new_row = {}
        for column in places_df.columns:
            if column in new_rows_df.columns:
                new_row.update({column: row[column]})
        # check if other country and # TODO: take care of the case of Other countries in the addressCountry[other] where addressCountry=oth
        if row["addressCountry"] == "-oth-":
            logger.warning(
                "A submission with Country Other requires attention by checking the extendedAddress"
            )
            new_row.update({"extendedAddress": row["addressCountry_other"]})
            # TODO_Update_Other_addressCountry

            #################################################################################

        # insert the row into the places df
        places_df.loc[len(places_df)] = new_row
        # logger.info('Print Tabulate of formatted places df of the new row.')
        # print(tabulate(places_df.iloc[-1:], headers='keys', tablefmt='psql'))

        # sort the rows of places df by addressCountry < addressRegion < addressLocality < name
        logger.info("Sorting places by Country, Region, Locality, Name")
        places_df = places_df.sort_values(
            by=["addressCountry", "addressRegion", "addressLocality", "name"],
            ascending=True,
        )
        # logger.info('Print Tabulate of formatted places df.')
        # print(tabulate(places_df, headers='keys', tablefmt='psql'))

        # write json and send a MR
        hash = hashlib.sha1()
        hash.update(str(time.time()).encode("utf-8"))
        mrf(
            "add-new-place-"
            + base64.b64encode(bytes(row["name"], "UTF-8")).decode("UTF-8")
            + "-"
            + hash.hexdigest()[:10],
            "Add place "
            + row["name"]
            + " from "
            + row["addressCountry"]
            + " to places.json",
            places_df,
            index,
        )  # index just for testing to be removed


else:
    logger.info("No new records were found")


# find a way to build the image once in advance and use it instead of rebuilding the image each time; saves timein order not to commit places.json
