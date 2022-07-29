import pandas as pd
import matplotlib.pyplot as plt
from benchart import Run, RunGroup
import matplotlib.gridspec as gridspec

class Result:
    def __init__(self, run, label_components=[]):
        self.run = run
        self.run_id = run.id
        self.df = pd.DataFrame(run.data)
        self.metadata = run.metadata
        if label_components:
            string = ', '.join(str(label_component) for label_component in label_components[1:])
            self.label += f' {string}'

    def plot(self, ax):
        self.df.plot(x='ts', y='tps', ax=ax, label=self.metadata['machine_id'])

    @property
    def label(self):
        prefix = f'Run {str(self.run_id)}'
        show_attrs = self.metadata.keys() - self.run.rungroup.accumulated_attrs
        if not show_attrs:
            return prefix
        return prefix + ' ' + str(self.metadata.subset(show_attrs))

class Renderer:
    def __init__(self, figure):
        self.figure = figure

class GridSpecRenderer(Renderer):
    def __call__(self, renderers, run_group, indent=0):
        renderer, *renderers = renderers

        self.figure.suptitle(run_group)
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
        label_components = []
        results = []
        # TODO: this shouldn't be happening, I think
        if isinstance(run_group, Run):
            results = [Result(run_group)]

        elif isinstance(run_group.children[0], Run):
            results = [Result(run) for run in run_group.children]
        else:
            results = self.flatten(run_group, label_components)

        for result in results:
            result.df.plot(x='ts', y='tps', ax=ax, label=result.label)

    def flatten(self, node, label_components):
        if isinstance(node, Run):
            return [Result(node, label_components)]

        output = []
        for child in node.children:
            t = self.flatten(child, label_components + [node])
            output.extend(t)
        return output
