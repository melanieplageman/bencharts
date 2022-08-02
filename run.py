import matplotlib.pyplot as plt
from renderer import SubGridSpecRenderer, GridSpecRenderer, AxesRenderer, \
PlotRenderer
import os
import sys
from benchart import BenchArt, Run
from metadata import RunMetadata
from loader import flatten, extract, normalize
import json

results_dir='run_data2'
runs = []
for i, datafile in enumerate(os.listdir(results_dir)):
    all_data = extract(os.path.join(results_dir, datafile))
    data = all_data['data']['pgbench']['progress']
    metadata = all_data['metadata']
    runs.append(Run(i + 1, data, RunMetadata(flatten(metadata)),
                    os.path.join(results_dir, datafile)))

normalize(runs)

benchart = BenchArt(runs)
# A no-op renderer until print_tree is made into a renderer
tree_renderer = None
benchart.part(tree_renderer, 'machine_instance_hostinfo_Hostname')
benchart.part(tree_renderer, 'machine_disk_size_gb')
benchart.part(tree_renderer, 'benchmark_config_scale')
benchart.ignore('machine_instance_hostinfo_KernelRelease',
                'machine_disk_block_device_settings_nr_hw_queues',
                'machine_disk_block_device_settings_nr_requests',
                'machine_disk_block_device_settings_queue_depth',
                'postgres_gucs_set_gucs_huge_pages',
                'machine_disk_block_device_settings_scheduler')
root = benchart.run()
benchart.print_tree(root)
