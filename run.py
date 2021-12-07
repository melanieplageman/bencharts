from benchart import BenchArt, Run
import pprint

data = {}
benchart = BenchArt([
    Run(1, data, {
        'machine_id': 223,
        'machine_os': 'Linux',
        'machine_location': 'local',
        'application_version': 12,
        'application_config_backend_flush_after': 128,
        'benchmark_name': 'pgbench',
        'benchmark_workload': 'tpcb'
        }
    ),
    Run(2, data, {
        'machine_id': 223,
        'machine_os': 'Linux',
        'machine_location': 'local',
        'application_version': 13,
        'application_config_backend_flush_after': 128,
        'benchmark_name': 'pgbench',
        'benchmark_workload': 'tpcb'
        }
    ),
    Run(3, data, {
        'machine_id': 223,
        'machine_os': 'Linux',
        'machine_location': 'local',
        'application_version': 12,
        'application_config_backend_flush_after': 256,
        'benchmark_name': 'pgbench',
        'benchmark_workload': 'tpcb'
        }
    ),
    Run(4, data, {
        'machine_id': 223,
        'machine_os': 'Linux',
        'machine_location': 'local',
        'application_version': 12,
        'application_config_backend_flush_after': 512,
        'benchmark_name': 'pgbench',
        'benchmark_workload': 'tpcb'
        }
    ),
    Run(5, data, {
        'machine_id': 222,
        'machine_os': 'Linux',
        'machine_location': 'local',
        'application_version': 12,
        'application_config_backend_flush_after': 512,
        'benchmark_name': 'pgbench',
        'benchmark_workload': 'tpcb'
        }
    ),
])

benchart.exhibit('application_version')
benchart.chart('application_config_backend_flush_after')

cohort = benchart.run()

for exhibit in cohort:
    pprint.pprint(exhibit)
    for chart in exhibit.charts:
        print(chart.special_run_print())

