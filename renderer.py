import pandas as pd
import matplotlib.pyplot as plt
from benchart import Run, RunGroup
import matplotlib.gridspec as gridspec

class Result:
    def __init__(self, run, relabels={}):
        self.run = run
        self.run_id = run.id
        self.df = pd.DataFrame(run.data)
        self.metadata = run.metadata
        self.relabels = relabels

    def plot(self, ax):
        self.df.plot(x='ts', y='tps', ax=ax, label=self.metadata['machine_id'])

    @property
    def label(self):
        prefix = f'Run {str(self.run_id)}'
        show_attrs = self.metadata.keys() - self.run.rungroup.accumulated_attrs
        if not show_attrs:
            return prefix
        subset = self.metadata.subset(show_attrs)

        result = ''
        for k, v in subset.items():
            key = k
            if k in self.relabels.keys():
                key = self.relabels[k]
            result += f'{key}: {v}, '

        return prefix + ': ' + result


class Renderer:
    def __init__(self, figure, relabels={}):
        self.figure = figure
        self.relabels = relabels

class GridSpecRenderer(Renderer):
    def __call__(self, renderers, run_group, indent=0):
        renderer, *renderers = renderers

        # TODO: use a javascript library to make this collapsible JSON
        # self.figure.suptitle(run_group)
        gridspec = self.figure.add_gridspec(nrows=len(run_group.children))
        print(" " * indent, f"add_gridspec(nrows={len(run_group.children)})")
        for i, child in enumerate(run_group.children):
            renderer(renderers, child, gridspec[i], indent + 2)

class SubGridSpecRenderer(Renderer):
    def __call__(self, renderers, run_group, cell, indent=0):
        renderer, *renderers = renderers

        subgridspec = cell.subgridspec(nrows=len(run_group.children), ncols=1)

        subfig = self.figure.add_subfigure(cell)
        subfig.suptitle(run_group, x=0.5, y=0.9)

        print(" " * indent, f"{cell}.subgridspec(nrows={len(run_group.children)})")
        for i, child in enumerate(run_group.children):
            renderer(renderers, child, subgridspec[i], indent + 2)


class AxesRenderer(Renderer):
    def __call__(self, renderers, run_group, cell, indent=0):
        renderer, *renderers = renderers

        print(" " * indent, f"figure.add_subplot({cell})")
        ax = self.figure.add_subplot(cell)
        ax.set_title(str(run_group))
        renderer(renderers, run_group, ax, indent + 2)


class PlotRenderer(Renderer):
    def __call__(self, renderers, run_group, ax, indent=0):
        results = []
        # TODO: this shouldn't be happening, I think
        if isinstance(run_group, Run):
            results = [Result(run_group, self.relabels)]

        elif isinstance(run_group.children[0], Run):
            results = [Result(run, self.relabels) for run in run_group.children]
        else:
            results = self.flatten(run_group)

        for result in results:
            result.df.plot(x='ts', y='tps', ax=ax, label=result.label)

    def flatten(self, node):
        if isinstance(node, Run):
            return [Result(node, self.relabels)]

        output = []
        for child in node.children:
            t = self.flatten(child)
            output.extend(t)
        return output
