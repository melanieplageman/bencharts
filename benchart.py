#!/usr/local/bin/python3

from metadata import RunMetadata
import copy

def map_runs(runs, attrs, shared=True):
    dictionary = {}
    for run in runs:
        if shared:
            dictionary.setdefault(run.metadata.shared_metadata(attrs), []).append(run)
        else:
            dictionary.setdefault(run.metadata.except_metadata(attrs), []).append(run)

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
        plot_label = self.metadata.except_metadata(label_attrs).pretty_print()
        return f'{plot_label} {self}\n'

class Chart:
    def __init__(self, exhibit_attrs, chart_attrs, shared_metadata, runs):
        self.chart_attrs = chart_attrs
        self.exhibit_attrs = exhibit_attrs

        self.runs = runs
        self.shared_metadata = shared_metadata

    @property
    def label(self):
        chart_labels = map_runs(self.runs, self.exhibit_attrs, shared=False).keys()
        return ''.join([chart_label.pretty_print() for chart_label in chart_labels])

    def __repr__(self):
        return f'Chart {self.label}'

    def special_run_print(self):
        out = f'{self}\n'
        for run in self.runs:
            out += run.label(self.chart_attrs)
        return out

class Exhibit:
    def __init__(self, eid, exhibit_attrs, chart_attrs):
        self.chart_attrs = chart_attrs
        self.exhibit_attrs = exhibit_attrs

        self.charts = []
        self.id = eid

    def __repr__(self):
        return f'Exhibit {self.id}'

    def make_charts(self, runs):
        chart_groups = map_runs(runs, self.chart_attrs)

        for shared_metadata, chart_group_runs in chart_groups.items():
            self.charts.append(Chart(self.exhibit_attrs, self.chart_attrs,
                shared_metadata,
                chart_group_runs))
        return self

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
                Exhibit(i, self.exhibit_attrs, self.chart_attrs
                        ).make_charts(all_exhibit_runs[i])
            )

        return exhibits
