import modules.scripts as scripts

import pandas as pd
import numpy as np
import os

from scripts.extra_helpers.tag_classes import TagSection, TagDict


def open_if_exists() -> list:
    global database_dict

    database_file_path = os.path.join(scripts.basedir(), r"a1111-sd-webui-tagcomplete\tags")
    if not os.path.isdir(database_file_path):
        return []

    databases = []
    for file in os.listdir(database_file_path):
        if file.endswith(".csv"):
            databases.append(pd.read_csv(os.path.join(database_file_path, file),
                                         na_values=["null"]).replace("", np.nan))

    return databases


def include_danbooru_tags(min_sections=4, max_categories=10):
    databases = open_if_exists()

    for database in databases:
        for key in list(database.keys()):
            print(f"next key = {key}")

