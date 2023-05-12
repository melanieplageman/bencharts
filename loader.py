#!/usr/bin/python3

from collections.abc import MutableMapping
import json
import os
import functools as ft
import pandas as pd
from metadata import RunMetadata
from benchart import Run, RunMetadata



class Loader:
    """
    Used to load files from a results directory and convert them to a series of
    Runs. User-defined expressions provide the loader with the proper way to
    extract metadata and data for the run.
    User-defined discard expressions applied to every file determine whether or
    not that file will be turned into a Run and appended to a list of runs.
    metadata from the input file is flattened. Nested JSON keys are joined
    together to create a composite key with a non-map value. This flattened
    metadata is made into the RunMetadata.
    Finally, Runs are normalized. Each RunMetadata's keys is replaced with the
    union of all distinct keys from all flattened RunMetadatas. The value of
    new keys added to RunMetadatas which were previously absent is an empty
    string.
    These two steps (flattening and normalizing) make it possible to diff and
    group Runs.
    """

    def __init__(self, root):
        self.root = root
        self.discards = []

    def discard(self, discard_expr, *args, **kwargs):
        self.discards.append((discard_expr, args, kwargs))

    def do_discard(self, all_info):
        return any(discard(all_info, *args, **kwargs) for discard, args, kwargs in self.discards)

    def run(self, data_exprs, metadata_expr, stats_expr, timeline):
        runs = []
        for i, datafile in enumerate(os.listdir(self.root)):
            all_info = extract(os.path.join(self.root, datafile))
            if self.do_discard(all_info):
                continue
            metadata = metadata_expr(all_info)
            stats = stats_expr(all_info)

            data = informed_extract_to_df(data_exprs, all_info, timeline)

            runs.append(Run(i + 1, data, RunMetadata(flatten(metadata)), stats,
                            os.path.join(self.root, datafile)))
        normalize(runs)
        return runs


def informed_extract_to_df(exprs, text, timeline):
    df_final = pd.DataFrame()

    for name, data_expr in exprs.items():
        data = data_expr(text)
        if not data:
            continue
        df = pd.DataFrame(data)
        df[timeline] = pd.to_datetime(df[timeline], utc=True)
        df = df.set_index(timeline)
        df = df.add_prefix(name + '_')

        df_final = pd.merge(df_final, df, how='outer', left_index=True, right_index=True)

    zero = df_final.index.min()
    df_final['relative_time'] = df_final.index - zero
    df_final = df_final.set_index('relative_time')

    return df_final


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
