#!/usr/local/bin/python3

import copy

def map_runs(runs, except_items):
    dictionary = {}
    for run in runs:
        run_string = ''.join(k + str(v) for k, v in run.metadata.items() if k not in except_items)
        dictionary.setdefault(run_string, []).append(run)
    return dictionary

class Run:
    def __init__(self, id, data, metadata):
        self.id = id
        self.data = data
        self.metadata = metadata

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
