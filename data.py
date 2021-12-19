import csv
from benchart import BenchArt, Run
from loader import flatten
import pprint
from metadata import RunMetadata

data = []
with open('data.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        data.append(row)

d1 = data[0:5]
d2 = data[5:10]
d3 = data[10:15]
d4 = data[15:20]
d5 = data[20:25]

run_list = [
        Run(1, d1, {
            'machine_id': 223,
            'machine_os': 'Linux',
            'machine_location': 'local',
            'hp': 'on',
            'application_version': 12,
            'application': {
                'config': { 'backend_flush_after': 128, },
            },
            'benchmark_name': 'pgbench',
            'benchmark_workload': 'tpcb'
            }
        ),
        Run(2, d2, {
            'machine_id': 223,
            'machine_os': 'Linux',
            'machine_location': 'local',
            'hp': 'on',
            'application_version': 13,
            'application': {
                'config': { 'backend_flush_after': 128, },
            },
            'benchmark_name': 'pgbench',
            'benchmark_workload': 'tpcb'
            }
        ),
        Run(3, d3, {
            'machine_id': 223,
            'machine_os': 'Linux',
            'machine_location': 'local',
            'hp': 'on',
            'application_version': 12,
            'application': {
                'config': { 'backend_flush_after': 256, },
            },
            'benchmark_name': 'pgbench',
            'benchmark_workload': 'tpcb'
            }
        ),
        Run(4, d4, {
            'machine_id': 223,
            'machine_os': 'Linux',
            'machine_location': 'local',
            'hp': 'on',
            'application_version': 12,
            'application': {
                'config': { 'backend_flush_after': 512, },
            },
            'benchmark_name': 'pgbench',
            'benchmark_workload': 'tpcb'
            }
        ),
        Run(5, d5, {
            'machine_id': 222,
            'machine_os': 'Linux',
            'machine_location': 'local',
            'hp': 'off',
            'application_version': 12,
            'application': {
                'config': { 'backend_flush_after': 512, },
            },
            'benchmark_name': 'pgbench',
            'benchmark_workload': 'tpcb'
            }
        ),
    ]

def make_benchart():
    for run in run_list:
        run.metadata = RunMetadata(flatten(run.metadata))
    return BenchArt(run_list)

