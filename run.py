import matplotlib.pyplot as plt
from renderer import SubGridSpecRenderer, GridSpecRenderer, AxesRenderer, \
PlotRenderer
import os
import sys
from benchart import BenchArt, Run
from metadata import RunMetadata
from loader import flatten, extract, normalize
import json




run_data=sys.argv[1]

runs = []
for i, datafile in enumerate(os.listdir(run_data)):
    all_data = extract(os.path.join(run_data, datafile))
    data = all_data['data']['pgbench']['progress']
    metadata = all_data['metadata']
    del metadata['postgres']['gucs']['all_gucs']
    del metadata['stats']
    runs.append(Run(i, data, RunMetadata(flatten(metadata))))

normalize(runs)

# print(json.dumps(runs[0].metadata.metadata))

benchart = BenchArt(runs)
root = benchart.run()
benchart.part('benchmark_config_num_clients')
benchart.print_tree(root)

figure = plt.figure(figsize=(5,10))
size = figure.get_size_inches()
renderers = [
        GridSpecRenderer(figure),
        SubGridSpecRenderer(figure),
        # SubGridSpecRenderer(figure),
        AxesRenderer(figure),
        PlotRenderer(figure)
        ]

renderers[0](renderers[1:], root)
