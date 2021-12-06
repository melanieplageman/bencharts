#!/usr/local/bin/python3

import copy
from collections.abc import Mapping

class RunMetadata(Mapping):
    def __init__(self, metadata):
        self.metadata = metadata

    def __getitem__(self, key):
        return self.metadata[key]

    def __iter__(self):
        return iter(self.metadata)

    def __len__(self):
        return len(self.metadata)

    def __eq__(self, other):
        return self.metadata == other.metadata

    def __hash__(self):
        return hash(frozenset(self.metadata.items()))

    def __repr__(self):
        return repr(self.metadata)

    def keys(self):
        return self.metadata.keys()

    def items(self):
        return self.metadata.items()

    def values(self):
        return self.metadata.values()

    def excepted_metadata(self, except_keys):
        return RunMetadata({ k: v for k, v in self.metadata.items() if k not in except_keys })

def map_runs(runs, except_items):
    dictionary = {}
    for run in runs:
        dictionary.setdefault(run.metadata.excepted_metadata(except_items), []).append(run)
    return dictionary

class Run:
    def __init__(self, id, data, metadata):
        self.id = id
        self.data = data
        self.metadata = RunMetadata(metadata)

    def __eq__(self, other):
        return self.metadata == other.metadata

    def __hash__(self):
        return hash(str(self.metadata))

    def __repr__(self):
        return "Run %s: %s\n" % (str(self.id), str(self.metadata))

class Chart:
    def __init__(self, attrs, runs):
        self.attrs = attrs
        self.runs = runs

    def __repr__(self):
        return f'Chart {self.attrs}'

class Exhibit:
    def __init__(self, eid, runs):
        self.id = eid
        self.runs = runs

    def __repr__(self):
        return f'Exhibit {self.id}'

class BenchArt:
    def __init__(self, runs):
        self.runs = runs
        self.exhibit_attrs = []
        self.chart_attrs = []

    def exhibit(self, key):
       self.exhibit_attrs.append(key) 

    def chart(self, key):
        self.chart_attrs.append(key)

    def run(self):
        exhibit_groups = map_runs(self.runs, self.exhibit_attrs + self.chart_attrs)
        
        exhibits = []
        all_exhibit_runs = list(exhibit_groups.values())
        for i in range(len(all_exhibit_runs)):
            exhibits.append(Exhibit(i,
                map_runs(all_exhibit_runs[i], self.chart_attrs)))

        return exhibits
