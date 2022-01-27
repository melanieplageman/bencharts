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

class Renderer:
    def __init__(self, figure):
        self.figure = figure

class GridSpecRenderer(Renderer):
    def __call__(self, renderers, run_group, indent=0):
        renderer, *renderers = renderers

        gridspec = self.figure.add_gridspec(nrows=len(run_group.children))
        print(" " * indent, f"add_gridspec(nrows={len(run_group.children)})")
        for i, child in enumerate(run_group.children):
            renderer(renderers, child, gridspec[i], indent + 2)

class SubGridSpecRenderer(Renderer):
    def __call__(self, renderers, run_group, cell, indent=0):
        renderer, *renderers = renderers

        subgridspec = cell.subgridspec(nrows=len(run_group.children), ncols=1)
        print(" " * indent, f"{cell}.subgridspec(nrows={len(run_group.children)})")
        for i, child in enumerate(run_group.children):
            renderer(renderers, child, subgridspec[i], indent + 2)

class AxesRenderer(Renderer):
    def __call__(self, renderers, run_group, cell, indent=0):
        renderer, *renderers = renderers

        print(" " * indent, f"figure.add_subplot({cell})")
        ax = self.figure.add_subplot(cell)
        renderer(renderers, run_group, ax, indent + 2)

class PlotRenderer(Renderer):
    def __call__(self, renderers, run_group, ax, indent=0):
        runs = []
        if isinstance(run_group.children[0], Run):
            runs = run_group.children
        else:
            self.flatten(run_group, runs)

        for run in runs:
            result = Result(run)
            result.df.plot(x='ts', y='tps', ax=ax, label=f'Run {str(run.id)}')

    def flatten(self, node, answers):
        if isinstance(node, Run):
            return node
        for child in node.children:
            t = self.flatten(child, answers)
            if t:
                answers.append(t)

def do_render(root):
    figure = plt.figure(figsize=(10,30))
    size = figure.get_size_inches()
    renderers = [
            GridSpecRenderer(figure),
            SubGridSpecRenderer(figure),
            SubGridSpecRenderer(figure),
            AxesRenderer(figure),
            PlotRenderer(figure)
            ]

    renderers[0](renderers[1:], root)
