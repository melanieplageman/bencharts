#!/usr/bin/python3

from collections.abc import MutableMapping
import json
from metadata import RunMetadata

# inspo from
# https://stackoverflow.com/questions/6027558/flatten-nested-dictionaries-compressing-keys

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
