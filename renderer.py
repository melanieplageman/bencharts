#!/usr/local/bin/python3

from datetime import timedelta
import pandas as pd
import matplotlib as mp
import matplotlib.pyplot as plt
from textwrap import wrap
from benchart import Run, RunGroup
import collections

DEBUG = False


class Renderer:
    def __init__(self, occludes=set(), relabels={}):
        # relabels are used on Metadata to make long metadata names shorter for
        # labels and titles.
        self.relabels = relabels
        self.occludes = occludes


class SubfigureRenderer(Renderer):
    """
    Renders RunGroups as nested subfigures in Matplotlib. Creates a subfigure
    for every RunGroup child of the passed-in run_group within the passed-in
    parent figure or subfigure.
    """
    def __call__(self, renderers, run_group, subfig, set_title=True, indent=0):
        renderer, *renderers = renderers

        if set_title:
            subfig.suptitle(do_relabel_str(run_group.metadata, self.relabels),
                            wrap=True)

        subfigs = subfig.subfigures(len(run_group.children), 1, wspace=0.07,
                                    hspace=0.05, frameon=True,
                                    edgecolor='black', linewidth=2,
                                    squeeze=False)

        for i, child in enumerate(run_group.children):
            renderer(renderers, child, subfigs[i][0],
                     indent=indent + 2)


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
            ax.set_title(do_relabel_str(run_group.metadata, self.relabels))

        renderer(renderers, run_group, ax, indent=indent + 2)


class PlotRenderer(Renderer):
    """
    Renders Runs as plots in Matplotlib. A Pandas DataFrame is created for
    every Run's data of the passed in Run or Run children of the passed-in
    RunGroup on the passed-in axis.
    """
    def __init__(self, *args, timebounds=(0, None), **kwargs):
        super().__init__(*args, **kwargs)
        self.timebounds = timebounds

    def __call__(self, renderers, run_group: Run | RunGroup, ax, subject=None, set_title=False, indent=0):
        if isinstance(run_group, Run):
            run = run_group
            df = run.all_data[self.timebounds[0]:self.timebounds[1]]
            df = df.interpolate(method='linear')
            if subject not in df.columns:
                return
            df.plot(y=subject, ax=ax, ylabel=subject, label=self.label(run))
            # Display each tick on the X axis as MM:SS
            ax.tick_params(axis='x', labelrotation=0)
            ax.xaxis.set_major_formatter(lambda x, _: "%02d:%02d" % (x // 60, x % 60))
            for label in ax.get_xticklabels():
                label.set_horizontalalignment('center')
            return

        if isinstance(run_group.children[0], Run):
            runs = run_group.children
        else:
            runs = self.flatten(run_group)

        # TODO: is there a less hacky way to make this work for both multi and
        # singular than hard-coding in the single column thing?
        for run in runs:
            if len(run.all_data.columns) == 0:
                continue
            self(None, run, ax, subject=run.all_data.columns[0], indent=indent + 2)

    def label(self, run):
        prefix = f'Run {str(run.id)}'
        show_attrs = run.metadata.keys() - run.rungroup.accumulated_attrs
        # Attributes which will be occluded must be passed as ignores into
        # BenchArt.ignore() so that they are not used in grouping Runs into
        # RunGroups. Occludes are not included in the final label for Runs in a
        # chart.
        if self.occludes:
            show_attrs -= self.occludes
        if not show_attrs:
            return prefix
        subset = run.metadata.subset(show_attrs)

        return prefix + ': ' + do_relabel_str(subset, self.relabels)

    def flatten(self, node):
        if isinstance(node, Run):
            return [node]

        output = []
        for child in node.children:
            output.extend(self.flatten(child))
        return output


def render(benchart, figure, timebounds, relabels):
    root = benchart.run()

    # The title often includes many shared attributes. This will be
    # displayed as collapsible JSON instead of using it as a title
    title = collections.OrderedDict(sorted(root.metadata.metadata.items()))

    renderers = [
        SubfigureRenderer(relabels),
        *benchart.renderers,
        AxesRenderer(relabels),
        PlotRenderer(timebounds=timebounds, occludes=benchart.ignores, relabels=relabels),
    ]

    renderers[0](renderers[1:], root, figure, set_title=False)
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


# TODO: figure out how to do this title better -- maybe by changing how
# accumulated_metadata works
def extra_title_expr(l):
    return ''

class LeafParentRenderer(Renderer):
    def __init__(self, root_metadata, *args, extra_title_expr=extra_title_expr, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra_title_expr = extra_title_expr
        self.root_metadata = root_metadata

    def __call__(self, renderers, run_group, sorted_prefixes=[], title=''):
        if isinstance(run_group, Run):
            return

        if hasattr(run_group, 'children') and isinstance(run_group.children[0], Run):
            renderer, *renderers = renderers
            cols = set()
            for child in run_group.children:
                cols.update(list(child.all_data.columns))

            title = self.extra_title_expr(run_group.children) + \
                run_group.accumulated_metadata.minus(self.root_metadata).pretty_print()

            cols = sorted(list(cols), key=lambda x: sorted_prefixes.index(x.split('_')[0]))
            renderer(renderers, run_group, cols, title=title)
        else:
            for child in run_group.children:
                self(renderers, child, sorted_prefixes)


class MultiAxesRenderer(Renderer):
    def __init__(self, axes_expr, *args, figwidth=15, **kwargs):
        super().__init__(*args, **kwargs)
        self.figwidth = figwidth
        self.axes_expr = axes_expr

    def __call__(self, renderers, run_group, axes_subjects, title=''):
        figure = plt.figure(figsize=(self.figwidth, len(axes_subjects) * 4))

        axes = {}
        first_ax = axes[axes_subjects[0]] = figure.add_subplot(len(axes_subjects), 1, 1)

        # Calculate the union of all timelines for this rungroup. We need to
        # find the limits of the combined timeline so that the location of the
        # ticks don't just depend on what happens to be plotted on first_ax.
        # The actual limit is set with axes.set_xlim() which has to be numeric
        # despite the fact that we're plotting a TimedeltaIndex.
        timeline = pd.TimedeltaIndex([])
        for run in run_group.iterruns():
            timeline = timeline.union(run.all_data.index)
        first_ax.set_xlim(xmin=0, xmax=timeline.max().total_seconds())

        for i, subject in enumerate(axes_subjects[1:], 2):
            axes[subject] = figure.add_subplot(len(axes_subjects), 1, i, sharex=first_ax)

        renderer, *renderers = renderers
        for subject in axes_subjects:
            for child in run_group.children:
                renderer(renderer, child, axes[subject], subject)

        axes[axes_subjects[0]].set_title("\n".join(wrap(title)))
        self.axes_expr(axes)


def render_multi(benchart, figwidth, sorted_prefixes, timebounds, relabels,
                  extra_title_expr, axes_expr):
    root = benchart.run()
    title = ''
    renderers = [
        LeafParentRenderer(root.metadata, relabels=relabels, extra_title_expr=extra_title_expr),
        MultiAxesRenderer(figwidth=figwidth, axes_expr=axes_expr),
        PlotRenderer(occludes=benchart.ignores, relabels=relabels,
                           timebounds=timebounds),
    ]
    renderers[0](renderers[1:], root, sorted_prefixes=sorted_prefixes, title='')
    return root, title
