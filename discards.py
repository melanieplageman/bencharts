import re

def discard_large_read(all_data, invert=False):
    large_read = all_data['metadata']['benchmark'].get('large_read', None)
    not_large_read = large_read is None or large_read == '' or large_read == 'none'
    result = not not_large_read
    return result if not invert else not result

def discard_host(all_data, target_hostname='vm-7', invert=False):
    hostname = all_data['metadata']['machine']['instance']['hostinfo']['Hostname']
    result = hostname == target_hostname
    return result if not invert else not result

def discard_vm(all_data, vm='Standard_D16ds_v4', invert=False):
    instance_type = all_data['metadata']['machine']['instance']['type']
    result = instance_type == vm
    return result if not invert else not result

def discard_disk_vm(all_data, disk='p40', vm='Standard_D16ds_v4', invert=False):
    instance_type = all_data['metadata']['machine']['instance']['type']
    disk_kind = all_data['metadata']['machine']['disk']['limits']['size']
    result = disk_kind == disk and instance_type == vm
    return result if not invert else not result

def discard_ultra(all_data, invert=False):
    disk_kind = all_data['metadata']['machine']['disk']['limits']['size']
    result = disk_kind == 'ultra1024'
    return result if not invert else not result

def discard_readonly(all_data, invert=False):
    caching = all_data['metadata']['machine']['disk']['caching']
    result = caching == 'ReadOnly'
    return result if not invert else not result

def discard_d2(all_data, invert=False):
    instance_type = all_data['metadata']['machine']['instance']['type']
    result = instance_type == 'Standard_D2ds_v4'
    return result if not invert else not result

def discard_scale(all_data, target_scale, invert=False):
    scale = all_data['metadata']['benchmark']['config']['scale']
    result = int(scale) == int(target_scale)
    return result if not invert else not result

def discard_kernel(all_data, version='5.18.5', invert=False):
    kernel_version = all_data['metadata']['machine']['instance']['hostinfo']['KernelRelease']
    result = kernel_version == version
    return result if not invert else not result

def discard_queue_depths(all_data, target_queue_depths=[128], invert=False):
    queue_depth = all_data['metadata']['machine']['disk']['block_device_settings']['queue_depth']
    result = queue_depth in target_queue_depths
    return result if not invert else not result

def discard_kernel_queue_depth(all_data, target_queue_depth,
                               target_kernel_version, invert=False):
    queue_depth = all_data['metadata']['machine']['disk']['block_device_settings']['queue_depth']
    kernel_version = all_data['metadata']['machine']['instance']['hostinfo']['KernelRelease']
    result = kernel_version == target_kernel_version and queue_depth == target_queue_depth
    return result if not invert else not result

def discard_scheduler(all_data, target_scheduler='mq-deadline', invert=False):
    scheduler = all_data['metadata']['machine']['disk']['block_device_settings']['scheduler']
    re_sched = re.compile(r"\[([a-zA-Z|-]*)\]")
    sched_match = re_sched.match(scheduler)
    result = sched_match is not None and sched_match.group(1) == target_scheduler
    return result if not invert else not result

def discard_hwq(all_data, target_hwq=1, invert=False):
    hwq = all_data['metadata']['machine']['disk']['block_device_settings']['nr_hw_queues']
    result = target_hwq == hwq
    return result if not invert else not result

def discard_kernel_hwq(all_data, target_hwq=1, target_kernel_version='5.18.5',
                       invert=False):
    hwq = all_data['metadata']['machine']['disk']['block_device_settings']['nr_hw_queues']
    kernel_version = all_data['metadata']['machine']['instance']['hostinfo']['KernelRelease']
    result = target_kernel_version == kernel_version and target_hwq == hwq
    return result if not invert else not result

def discard_nr_requests(all_data, target_nr_requests, invert=False):
    nr_requests = all_data['metadata']['machine']['disk']['block_device_settings']['nr_requests']
    result = nr_requests == target_nr_requests
    return result if not invert else not result

def discard_non_default_old_kernel_d2(all_data, invert=False):
    kernel_version = all_data['metadata']['machine']['instance']['hostinfo']['KernelRelease']
    hwq = all_data['metadata']['machine']['disk']['block_device_settings']['nr_hw_queues']
    nr_requests = all_data['metadata']['machine']['disk']['block_device_settings']['nr_requests']
    queue_depth = all_data['metadata']['machine']['disk']['block_device_settings']['queue_depth']
    scheduler = all_data['metadata']['machine']['disk']['block_device_settings']['scheduler']
    re_sched = re.compile(r"\[([a-zA-Z|-]*)\]")
    sched_match = re_sched.match(scheduler)
    if kernel_version == '5.18.5+':
        return False
    result = kernel_version != '5.18.5' or hwq != 2 or nr_requests != 316 or queue_depth != 316 or sched_match.group(1) != 'none'
    return result if not invert else not result
