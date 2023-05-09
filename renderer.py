#!/usr/local/bin/python3

import pandas as pd
import matplotlib.pyplot as plt
from benchart import Run, RunGroup
import collections

DEBUG = False

class Result:
    def __init__(self, run, timebounds=(0,None), relabels={}):
        self.run = run
        self.run_id = run.id
        self.df = run.all_data
        self.metadata = run.metadata
        self.relabels = relabels
        self.timebounds = timebounds

    def plot(self, ax, y, label):
        df = self.df[self.timebounds[0]:self.timebounds[1]]
        df = df.interpolate(method='linear')
        df.plot(y=y, ax=ax, label=label)


class MultiResult(Result):
    def __init__(self, *args, occludes=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.occludes = occludes

    def plot(self, axes, all_ys, timebounds, sharex):
        for key in self.df.columns:
            if key not in all_ys:
                continue
            df = self.df[timebounds[0]:timebounds[1]]
            df = df.interpolate(method='linear')
            df.plot(y=key, ax=axes[key], ylabel=key,
                    sharex=sharex, label=self.label())

    # TODO: this is basically the same as the PlotRenderer, so perhaps we can
    # subclass that or somehow make render_multi() more normal
    def label(self):
        prefix = f'Run {str(self.run_id)}'
        show_attrs = self.metadata.keys() - self.run.rungroup.accumulated_attrs
        # Attributes which will be occluded must be passed as ignores into
        # BenchArt.ignore() so that they are not used in grouping Runs into
        # RunGroups. Occludes are not included in the final label for Runs in a
        # chart.
        if self.occludes:
            show_attrs -= self.occludes
        if not show_attrs:
            return prefix
        subset = self.metadata.subset(show_attrs)
        return prefix + ': ' + do_relabel_str(subset, self.relabels)


class Renderer:
    def __init__(self, relabels={}):
        # relabels are used on Metadata to make long metadata names shorter for
        # labels and titles.
        self.relabels = relabels


class SubfigureRenderer(Renderer):
    """
    Renders RunGroups as nested subfigures in Matplotlib. Creates a subfigure
    for every RunGroup child of the passed-in run_group within the passed-in
    parent figure or subfigure.
    """
    def __call__(self, renderers, run_group, subfig, timebounds=(0,None), set_title=True, indent=0):
        renderer, *renderers = renderers

        if set_title:
            subfig.suptitle(do_relabel_str(run_group.metadata, self.relabels),
                            wrap=True)

        subfigs = subfig.subfigures(len(run_group.children), 1, wspace=0.07,
                                    hspace=0.05, frameon=True,
                                    edgecolor='black', linewidth=2,
                                    squeeze=False)

        for i, child in enumerate(run_group.children):
            renderer(renderers, child, subfigs[i][0], timebounds=timebounds,
                     indent=indent + 2)


class AxesRenderer(Renderer):
    """
    Renders RunGroups as axes in Matplotlib. Creates an axes (via adding a
    subplot) for every child of the passed-in RunGroup within the passed-in
    subfigure.
    """
    def __call__(self, renderers, run_group, subfig, timebounds=(0,None), set_title=True, indent=0):
        renderer, *renderers = renderers

        ax = subfig.add_subplot()
        if set_title:
            ax.set_title(do_relabel_str(run_group.metadata, self.relabels))

        renderer(renderers, run_group, ax, timebounds=timebounds, indent=indent + 2)


class PlotRenderer(Renderer):
    """
    Renders Runs as plots in Matplotlib. A Pandas DataFrame is created for
    every Run's data of the passed in Run or Run children of the passed-in
    RunGroup on the passed-in axis.
    """
    def __init__(self, all_ys, *args, occludes=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.occludes = occludes
        self.all_ys = all_ys

    def __call__(self, renderers, run_group: Run | RunGroup, ax, timebounds=(0,None), set_title=False, indent=0):
        results = []
        if isinstance(run_group, Run):
            results = [Result(run_group, timebounds, self.relabels)]

        elif isinstance(run_group.children[0], Run):
            results = [Result(run, timebounds, self.relabels) for run in run_group.children]
        else:
            results = self.flatten(run_group, timebounds)

        for result in results:
            result.plot(ax=ax, y=self.all_ys[0], label=self.label(result))

        # Display each tick on the X axis as MM:SS
        ax.xaxis.set_major_formatter(lambda x, pos: "%02d:%02d" % (x // 60, x % 60))
        filenames = {result.run_id: result.run.filename for result in results}
        pdf = pd.Series(filenames)
        pd.set_option('display.max_colwidth', None)
        # print(pdf)

    # TODO: perhaps this can be moved into the result?
    def label(self, result):
        prefix = f'Run {str(result.run_id)}'
        show_attrs = result.metadata.keys() - result.run.rungroup.accumulated_attrs
        # Attributes which will be occluded must be passed as ignores into
        # BenchArt.ignore() so that they are not used in grouping Runs into
        # RunGroups. Occludes are not included in the final label for Runs in a
        # chart.
        if self.occludes:
            show_attrs -= self.occludes
        if not show_attrs:
            return prefix
        subset = result.metadata.subset(show_attrs)

        return prefix + ': ' + do_relabel_str(subset, result.relabels)

    def flatten(self, node, timebounds):
        if isinstance(node, Run):
            return [Result(node, timebounds, self.relabels)]

        output = []
        for child in node.children:
            output.extend(self.flatten(child, timebounds))
        return output


def render(benchart, figure, all_ys, timebounds, relabels):
    root = benchart.run()

    # The title often includes many shared attributes. This will be
    # displayed as collapsible JSON instead of using it as a title
    title = collections.OrderedDict(sorted(root.metadata.metadata.items()))

    renderers = [
        SubfigureRenderer(relabels),
        *benchart.renderers,
        AxesRenderer(relabels),
        PlotRenderer(all_ys, relabels, occludes=benchart.ignores),
    ]

    renderers[0](renderers[1:], root, figure, timebounds, set_title=False)
    return root, title

def do_relabel_str(metadata, relabels):
    result = ''
    for k, v in metadata.items():
        key = k
        if k in relabels.keys():
            key = relabels[k]
        result += f'{key}: {v}, '
    return result

def do_relabel_tree(metadata, relabels):
    result = {}
    for k, v in metadata.items():
        key = k
        if k in relabels.keys():
            key = relabels[k]
        result[key] = v
    return result

def render_print_tree(root, occludes=None, relabels=None, indent=0):
    if isinstance(root, Run):
        display = f"{str(root)}: "
        show_attrs = root.metadata.keys() - root.rungroup.accumulated_attrs
        if show_attrs:
            if occludes:
                show_attrs -= occludes
            subset = root.metadata.subset(show_attrs)
            attributes = str(subset)
            if relabels:
                attributes = str(do_relabel_tree(subset, relabels))
            display += attributes
        print(" " * indent + display)
        return

    if relabels:
        root.metadata = do_relabel_tree(root.metadata, relabels)

    print(" " * indent + str(root))

    for node in root.children:
        render_print_tree(node, occludes, relabels, indent + 2)

# TODO: render_multi() should subclass a Renderer probably
def render_multi(benchart, all_ys, timebounds, figsize, extra_title_expr):
    root = benchart.run()
    all_axes = []
    # Since we are making a new figure and set of axes for each leaf parent, we
    # can't use a DFT to plot this. We could do a BFT but it seems easier to
    # just get all the leaf parents in a list and then plot their runs.
    leaf_parents = []
    get_all_leaf_parents(root, leaf_parents)
    for parent in leaf_parents:
        figure = plt.figure(figsize=figsize)
        axes = {}
        for i, key in enumerate(all_ys, 1):
            axes[key] = figure.add_subplot(len(all_ys), 1, i)
        axes[all_ys[0]].set_title(
            extra_title_expr(parent.children) + \
            parent.accumulated_metadata.minus(root.metadata).pretty_print()
        )

        for child in parent.children:
            result = MultiResult(child, occludes=benchart.ignores)
            result.plot(axes, all_ys, timebounds, sharex=axes[all_ys[0]])
        all_axes.append(axes)
    return all_axes

# TODO: make this not mutate the list probably
def get_all_leaf_parents(node, leaf_parents):
    if hasattr(node, 'children') and isinstance(node.children[0], Run):
        leaf_parents.append(node)
        return
    for child in node.children:
        get_all_leaf_parents(child, leaf_parents)
