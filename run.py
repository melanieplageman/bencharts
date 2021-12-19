from benchart import BenchArt, Run
import pprint
from data import make_benchart

benchart = make_benchart()
benchart.part('application_version')
benchart.part('application_config_backend_flush_after')

root = benchart.run()

print(benchart.print_tree(root))
