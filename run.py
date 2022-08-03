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

disk_identifier = ['machine_disk_limits_burst_iops',
                   'machine_disk_limits_iops', 'machine_disk_limits_size',
                   'machine_disk_limits_burst_bw_mbps',
                   'machine_disk_limits_bw_mbps', 'machine_disk_size_gb', ]

benchart.part(tree_renderer, 'machine_instance_hostinfo_Hostname',
              'machine_instance_type', *disk_identifier)


benchart.part(tree_renderer, 'benchmark_config_scale')
benchart.part(tree_renderer, 'benchmark_large_read')


benchart.ignore('machine_instance_hostinfo_KernelRelease',
                'machine_disk_block_device_settings_nr_hw_queues',
                'machine_disk_block_device_settings_nr_requests',
                'machine_disk_block_device_settings_queue_depth',
                'machine_disk_block_device_settings_scheduler',
                'postgres.gucs.set_gucs.huge_pages')

root = benchart.run()
benchart.print_tree(root)
