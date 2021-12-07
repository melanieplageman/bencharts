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

    def shared_metadata(self, except_keys):
        return RunMetadata({ k: v for k, v in self.metadata.items() if k not in except_keys })

def map_runs(runs, except_items):
    dictionary = {}
    for run in runs:
        dictionary.setdefault(run.metadata.shared_metadata(except_items), []).append(run)
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

    def label(self, label_attrs):
        out = ''
        for k, v in self.metadata.items():
            if k in label_attrs:
                out += f' {k}: {v}\n'
        out += f'{self}\n'
        return out

class Chart:
    def __init__(self, exhibit_attrs, chart_attrs, chart_group_metadata, runs):
        self.chart_attrs = chart_attrs
        self.exhibit_attrs = exhibit_attrs
        self.runs = runs
        self.chart_group_metadata = chart_group_metadata

    @property
    def label(self):
        label = ''
        for k, v in self.chart_group_metadata.items():
            if k in self.exhibit_attrs:
                label += f' {k}: {v}'
        return label

    def __repr__(self):
        return f'Chart {self.label}'

    def special_run_print(self):
        out = f'{self}\n'
        for run in self.runs:
            out += run.label(self.chart_attrs)
        return out

class Exhibit:
    def __init__(self, eid, exhibit_attrs, chart_attrs, runs):
        self.id = eid
        self.chart_groups = map_runs(runs, chart_attrs)
        self.charts = []
        chart_label_attrs = []
        for attr in exhibit_attrs:
            if attr not in chart_attrs:
                chart_label_attrs.append(attr)

        for chart_group_metadata, chart_group_runs in self.chart_groups.items():
            self.charts.append(Chart(chart_label_attrs, chart_attrs,
                chart_group_metadata,
                chart_group_runs))

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
            exhibits.append(
                Exhibit(i, self.exhibit_attrs, self.chart_attrs, all_exhibit_runs[i])
            )

        return exhibits
