import csv
from benchart import BenchArt, Run
from loader import flatten
import pprint
from metadata import RunMetadata

run_list = [
        Run(1, 'data0.csv', {
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
        Run(2, 'data1.csv', {
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
        Run(3, 'data2.csv', {
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
        Run(4, 'data3.csv', {
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
        Run(5, 'data4.csv', {
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

