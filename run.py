import matplotlib.pyplot as plt
from renderer import render_print_tree
from benchart import BenchArt
from loader import Loader
from discards import *


load_root = 'run_data'

relabels = {
    'machine_instance_hostinfo_Hostname': 'host',
    'benchmark_config_scale': 'scale',
    'machine_instance_hostinfo_KernelRelease': 'kernel',
    'machine_disk_block_device_settings_nr_hw_queues': '#hwq',
    'machine_disk_block_device_settings_nr_requests': 'nr_requests',
    'machine_disk_block_device_settings_queue_depth': 'queue_depth',
    'machine_disk_block_device_settings_scheduler': 'scheduler',
    'postgres.gucs.set_gucs.huge_pages': 'huge_pages',
    'machine_disk_limits_size': 'disk_kind',
    'machine_disk_size_gb': 'disk_size_gb',
    'machine_instance_hostinfo_Hostname': 'host',
    'machine_instance_type': 'instance_type',
    'benchmark_config_scale': 'pgbench_scale',
}

ignores = ['machine_instance_hostinfo_KernelRelease',
                'machine_disk_block_device_settings_nr_hw_queues',
                'machine_disk_block_device_settings_nr_requests',
                'machine_disk_block_device_settings_queue_depth',
                'machine_disk_block_device_settings_scheduler']

occludes=set(['benchmark_config_time',
              'postgres_load_data',
              'postgres_init',
              'postgres_version',
              'postgres_gucs_set_gucs_huge_pages',
              'machine_disk_limits_burst_iops',
              'machine_disk_trim',
              'machine_disk_limits_iops',
              'machine_disk_limits_burst_bw_mbps',
              'machine_disk_limits_bw_mbps',
              'machine_instance_limits_uncached_burst_iops',
              'machine_instance_limits_uncached_iops',
              'machine_instance_limits_uncached_burst_bw_mbps',
              'machine_instance_limits_uncached_bw_mbps',
              'machine_instance_mem_total_bytes',
             ])

disk_identifier = ['machine_disk_size_gb', 'machine_disk_limits_size']

def data_def(all_data):
    return all_data['data']['pgbench']['progress']

def metadata_def(all_data):
    return all_data['metadata']

loader = Loader(load_root)
loader.discard(discard_disk_vm, disk='p40', vm='Standard_D16ds_v4', invert=True)
loader.discard(discard_readonly)

runs = loader.run(data_def, metadata_def)

benchart = BenchArt(runs)

# A no-op renderer
tree_renderer = None

benchart.part(tree_renderer, 'machine_instance_hostinfo_Hostname',
              'machine_instance_type', *disk_identifier)
benchart.part(tree_renderer, 'benchmark_large_read')
benchart.part(tree_renderer, 'benchmark_config_scale')

benchart.ignore(*ignores, *occludes)

root = benchart.run()

render_print_tree(root, occludes=occludes, relabels=relabels)
