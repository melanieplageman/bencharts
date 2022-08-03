#!/usr/bin/python3

from collections.abc import MutableMapping
import json
from metadata import RunMetadata
import os
from benchart import Run, RunMetadata

# inspo from
# https://stackoverflow.com/questions/6027558/flatten-nested-dictionaries-compressing-keys


class Loader:
    """Used to load a results directory into a series of Runs."""

    def __init__(self, root):
        self.root = root
        self.discards = []

    def discard(self, discard_expr):
        self.discards.append(discard_expr)

    def do_discard(self, all_data):
        return any(discard(all_data) for discard in self.discards)

    def run(self, data_expr, metadata_expr):
        runs = []
        for i, datafile in enumerate(os.listdir(self.root)):
            all_data = extract(os.path.join(self.root, datafile))
            data = data_expr(all_data)
            metadata = metadata_expr(all_data)
            if self.do_discard(all_data):
                continue
            runs.append(Run(i + 1, data, RunMetadata(flatten(metadata)),
                            os.path.join(self.root, datafile)))


        normalize(runs)
        return runs

# TODO: handle arrays
def flatten(dictionary, parent_key=''):
    result = {}
    for k, v in dictionary.items():
        new_key = parent_key + '_' + k if parent_key else k
        if isinstance(v, MutableMapping):
            result.update(flatten(v, parent_key=new_key))
        else:
            result[new_key] = v
    return result

def extract(file):
    output = {}
    with open(file) as f:
        output = json.load(f)
    return output

def normalize(runs):
    all_attrs = set()
    for run in runs:
        all_attrs.update(run.metadata.keys())

    base_metadata = {
        attr: '' for attr in all_attrs
    }

    for run in runs:
        run.metadata = RunMetadata({**base_metadata, **run.metadata})
