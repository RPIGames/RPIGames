"""
Loader for the files in this directory.

Due to how python imports work, this file will only run once and
provide both the adjective_list and noun_list in memory for other
modules in the package.
"""

import os.path
from pathlib import Path

list_folder = Path(__file__).resolve().parent

adjective_list: list[str] = []
with open(os.path.join(list_folder, "english-adjectives.txt")) as f:
    for line in f.readlines():
        adjective_list.append(line.strip().lower())

noun_list: list[str] = []
with open(os.path.join(list_folder, "english-nouns.txt")) as f:
    for line in f.readlines():
        noun_list.append(line.strip().lower())
