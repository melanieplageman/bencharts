import pandas as pd
import matplotlib.pyplot as plt
from benchart import Run, RunGroup
import matplotlib.gridspec as gridspec

class Result:
    def __init__(self, run):
        self.run_id = run.id
        dtypes = {'ts': 'str', 'tps': 'float', 'lat': 'float', 'stddev': 'float'}
        # Assuming run.data is a CSV filename for now
        self.df = pd.read_csv(run.data, dtype=dtypes, parse_dates=['ts'])
        self.metadata = run.metadata

    def plot(self, ax):
        self.df.plot(x='ts', y='tps', ax=ax, label=self.metadata['machine_id'])

def do_render(root):
    if isinstance(root, Run):
        print("can't plot single Run with no other information")
        return
    if not root.children:
        print("Can't plot node with no runs")
        return
    figure = plt.figure(figsize=(10,30))
    size = figure.get_size_inches()
    #renderers = [render_gridspec, render_subgridspec, render_axes, plot]
    #renderers = [render_gridspec, render_subgridspec, render_subgridspec, render_axes, plot]
    renderers = [render_gridspec, render_axes, plot]
    render_gridspec(renderers[1:], root, figure)

def flatten(node, result):
    if isinstance(node, Run):
        return node
    for child in node.children:
        t = flatten(child, result)
        if t:
            result.append(t)

def render_gridspec(renderers, run_group, figure, indent=0):
    renderer, *renderers = renderers

    gridspec = figure.add_gridspec(nrows=len(run_group.children))
    print(" " * indent, f"add_gridspec(nrows={len(run_group.children)})")
    for i, child in enumerate(run_group.children):
        renderer(renderers, child, figure, gridspec[i], indent + 2)

def render_subgridspec(renderers, run_group, figure, cell, indent=0):
    renderer, *renderers = renderers

    subgridspec = cell.subgridspec(nrows=len(run_group.children), ncols=1)
    print(" " * indent, f"{cell}.subgridspec(nrows={len(run_group.children)})")
    for i, child in enumerate(run_group.children):
        renderer(renderers, child, figure, subgridspec[i], indent + 2)

def render_axes(renderers, run_group, figure, cell, indent=0):
    renderer, *renderers = renderers

    print(" " * indent, f"figure.add_subplot({cell})")
    ax = figure.add_subplot(cell)
    renderer(renderers, run_group, ax, indent + 2)

def plot(renderers, run_group, ax, indent=0):
    runs = []
    if isinstance(run_group.children[0], Run):
        runs = run_group.children
    else:
        flatten(run_group, runs)

    for run in runs:
        result = Result(run)
        result.df.plot(x='ts', y='tps', ax=ax, label=f'Run {str(run.id)}')
