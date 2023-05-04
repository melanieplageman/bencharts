#!/usr/local/bin/python3

from metadata import RunMetadata
import pprint

class Run:
    """
    The data and metadata produced by a single instance of running a benchmark.
    """
    def __init__(self, id, all_data, metadata, filename):
        self.id = id
        self.all_data = all_data
        self.metadata = RunMetadata(metadata)
        self.rungroup = None
        self.filename = filename

    def __eq__(self, other):
        if not isinstance(other, Run):
            return NotImplemented
        return self.metadata == other.metadata

    def __hash__(self):
        return hash(str(self.metadata))

    def __repr__(self):
        return "Run %s" % (str(self.id))


class Step:
    """
    A set of attributes used at once to evaluate the equality of Runs in a
    RunGroup.
    """
    def __init__(self, attrs):
        self.attrs = attrs

    # return a list of output groups
    def use(self, parent):
        output_groups = {}
        for run in parent.children:
            output_groups.setdefault(run.metadata.subset(self.attrs), []).append(run)

        result_rgs = [RunGroup(parent, sm, runs) for sm, runs in output_groups.items()]
        parent.children = result_rgs
        return result_rgs

    def __repr__(self):
        return f'Step attributes: {self.attrs}'


class IgnoreStep(Step):
    """
    A wrapper Step which precludes attributes specified by the user as
    "ignored" from being used when grouping Runs in a RunGroup
    """
    def use(self, parent):
        return []


class RunGroup:
    """
    A grouping of Runs which share certain metadata attributes
    """
    def __init__(self, parent, shared_metadata, children=None):
        self.metadata = shared_metadata
        self.parent = parent
        self.children = children or []

        # Hack so that the accumulated_attrs property works to make a label for
        # Runs. A Run sets itself as its RunGroup. Then when making its label,
        # it calculates the accumulated_attrs -- which are all of the
        # attributes of all of its parent tree RunGroups, including the root
        # which has all of the shared attributes for all Runs.
        # The difference between the accumulated_attrs and the Run metadata are
        # all the attributes which differ amongst runs but have not been use to
        # group RunGroups. These will be the Run ID itself and any attributes
        # added to the list of attributes to ignore while partitoning.
        # Going forward, there may be a better way to do this.
        for rungroup_or_run in self.children:
            if isinstance(rungroup_or_run, Run):
                rungroup_or_run.rungroup = self

    def __repr__(self):
        return f'Metadata: {self.metadata}'

    @property
    def accumulated_attrs(self):
        result = set(self.metadata.keys())
        if self.parent is not None and self.parent.metadata is not None:
            result |= self.parent.accumulated_attrs
        return result

    def iterruns(self):
        for child in self.children:
            if isinstance(child, Run):
                yield child
            else:
                yield from child.iterruns()


class BenchArt:
    """
    A tree whose non-leaf nodes are RunGroups and leaf nodes are Runs.
    The user creates a BenchArt using a list of Runs with properly prepared
    RunMetadata.
    The user then partitions the BenchArt specifying target attributes and
    Renderers for each partition.
    Any attributes which the user would like to exclude from the grouping
    process when creating the tree are specified during the "ignore" step.
    Steps created during partitioning are run.
    The tree has three "layers" (though it may have many more "levels" composed
    of sibling RunGroups). The first layer is all attributes on which all Runs
    agree. The second is all attributes which are neither agreed upon by all
    nor in the user-specified partitioning attributes. The third layer of
    RunGroups is all the user-specified attributes. This layer may be composed
    of many levels of sibling RunGroups.
    After running the BenchArt, the tree of RunGroups can be rendered.
    """
    def __init__(self, runs):
        # A list of Runs
        self.runs = runs
        # We assume loader has standardized all runs to have the same keys
        self.all_attrs = runs[0].metadata.keys()
        self.user_steps = []
        self.renderers = []

    # these must be appended in order
    def part(self, renderer, *attrs):
        self.renderers.append(renderer)
        self.user_steps.append(Step(set(attrs)))

    # What the user actually wants to compare
    def versus(self, *attrs):
        return self.user_steps.append(IgnoreStep(set(attrs)))

    # All attributes which won't be used when grouping Runs into RunGroups
    def ignore(self, *attrs):
        return self.user_steps.append(IgnoreStep(set(attrs)))

    # returns a set of string, which are the attributes on which all runs agree
    # e.g. {"ver", "hp"}
    def get_all_shared_attrs(self):
        all_shared_attrs = set()
        for attr in self.all_attrs:
            value = self.runs[0].metadata[attr]
            if all(run.metadata[attr] == value for run in self.runs):
                all_shared_attrs.add(attr)

        return all_shared_attrs

    def run(self):
        # a list of set(str), for example [{"ver", "hp"}, {"bfa"}]
        steps = []
        # Find all the attributes on which all runs agree
        all_shared_attrs = self.get_all_shared_attrs()
        steps.append(Step(all_shared_attrs))

        # Find all the attributes which are neither agreed upon by all nor in
        # user-specified attributes
        all_user_specified_attrs = set()
        for user_step in self.user_steps:
            all_user_specified_attrs.update(user_step.attrs)
        steps.append(Step(self.all_attrs - all_shared_attrs - all_user_specified_attrs))

        # add all user-specified attributes -- these must be in order
        steps += self.user_steps

        og = RunGroup(None, None, self.runs)
        groups = [og]

        for step in steps:
            current_level = []
            for group in groups:
                current_level.extend(step.use(group))
            groups = current_level

        return og.children[0]
