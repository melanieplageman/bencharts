import pandas as pd
import matplotlib.pyplot as plt
from benchart import Run
import collections

DEBUG = False

def do_relabel(metadata, relabels):
    result = ''
    for k, v in metadata.items():
        key = k
        if k in relabels.keys():
            key = relabels[k]
        result += f'{key}: {v}, '
    return result


class Result:
    def __init__(self, run, relabels={}):
        self.run = run
        self.run_id = run.id
        self.df = pd.DataFrame(run.data)

        self.metadata = run.metadata
        self.relabels = relabels

        self.df['ts'] = pd.to_datetime(self.df['ts'])
        zero = self.df['ts'].min()
        self.df['relative_time'] = (self.df['ts'] - zero).apply(
            lambda t: t.total_seconds())

    def plot(self, ax):
        self.df.plot(x='ts', y='tps', ax=ax, label=self.metadata['machine_id'])

    @property
    def label(self):
        prefix = f'Run {str(self.run_id)}'
        show_attrs = self.metadata.keys() - self.run.rungroup.accumulated_attrs
        if not show_attrs:
            return prefix
        subset = self.metadata.subset(show_attrs)

        return prefix + ': ' + do_relabel(subset, self.relabels)


class Renderer:
    def __init__(self, relabels={}):
        self.relabels = relabels


class SubfigureRenderer(Renderer):
    """
    Renders RunGroups as nested subfigures in Matplotlib. Creates a subfigure
    for every RunGroup child of the passed-in run_group within the passed-in
    parent figure or subfigure.
    """
    def __call__(self, renderers, run_group, subfig, set_title=True, indent=0):
        renderer, *renderers = renderers

        if set_title:
            subfig.suptitle(do_relabel(run_group.metadata, self.relabels),
                            wrap=True)

        subfigs = subfig.subfigures(len(run_group.children), 1, wspace=0.07,
                                    hspace=0.05, frameon=True,
                                    edgecolor='black', linewidth=2,
                                    squeeze=False)

        for i, child in enumerate(run_group.children):
            renderer(renderers, child, subfigs[i][0], indent + 2)


class AxesRenderer(Renderer):
    """
    Renders RunGroups as axes in Matplotlib. Creates an axes (via adding a
    subplot) for every child of the passed-in RunGroup within the passed-in
    subfigure.
    """
    def __call__(self, renderers, run_group, subfig, set_title=True, indent=0):
        renderer, *renderers = renderers

        ax = subfig.add_subplot()
        if set_title:
            ax.set_title(do_relabel(run_group.metadata, self.relabels))

        renderer(renderers, run_group, ax, indent + 2)


class PlotRenderer(Renderer):
    """
    Renders Runs as plots in Matplotlib. A Pandas DataFrame is created for
    every Run's data of the passed in Run or Run children of the passed-in
    RunGroup on the passed-in axis.
    """
    def __call__(self, renderers, run_group, ax, set_title=False, indent=0):
        results = []
        if isinstance(run_group, Run):
            results = [Result(run_group, self.relabels)]

        elif isinstance(run_group.children[0], Run):
            results = [Result(run, self.relabels) for run in run_group.children]
        else:
            results = self.flatten(run_group)

        for result in results:
            result.df.plot(x='relative_time', y='tps', ax=ax, label=result.label)

        # Display each tick on the X axis as MM:SS
        ax.xaxis.set_major_formatter(lambda x, pos: "%02d:%02d" % (x // 60, x % 60))
        filenames = {result.run_id: result.run.filename for result in results}
        pdf = pd.Series(filenames)
        print(pdf)


    def flatten(self, node):
        if isinstance(node, Run):
            return [Result(node, self.relabels)]

        output = []
        for child in node.children:
            output.extend(self.flatten(child))
        return output

def render(benchart, figure, relabels):
    root = benchart.run()

    # The title often includes many shared attributes. This will be
    # displayed as collapsible JSON instead of using it as a title
    title = collections.OrderedDict(sorted(root.metadata.metadata.items()))

    renderers = [
        SubfigureRenderer(relabels),
        *benchart.renderers,
        AxesRenderer(relabels),
        PlotRenderer(relabels),
    ]

    renderers[0](renderers[1:], root, figure, set_title=False)
    benchart.print_tree(root)
    return title
