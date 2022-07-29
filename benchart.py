#!/usr/local/bin/python3

from metadata import RunMetadata
import pprint

class Run:
    def __init__(self, id, data, metadata):
        self.id = id
        self.data = data
        self.metadata = RunMetadata(metadata)

    def __eq__(self, other):
        if not isinstance(other, Run):
            return NotImplemented
        return self.metadata == other.metadata

    def __hash__(self):
        return hash(str(self.metadata))

    def __repr__(self):
        return "Run %s" % (str(self.id))

class Step:
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

class RunGroup:
    def __init__(self, parent, shared_metadata, children=None):
        self.metadata = shared_metadata
        self.parent = parent
        self.children = children or []

    def __repr__(self):
        return f'Metadata: {self.metadata}'

class BenchArt:
    def __init__(self, runs):
        self.runs = runs
        # We assume loader has standardized all runs to have the same keys
        self.all_attrs = runs[0].metadata.keys()
        self.user_steps = []

    # these must be appended in order
    def part(self, *attrs):
        self.user_steps.append(Step(set(attrs)))

    # returns a set of string, which are the attributes on which all runs agree
    # e.g. {"ver", "hp"}
    def get_all_shared_attrs(self):
        all_shared_attrs = set()
        for attr in self.all_attrs:
            value = self.runs[0].metadata[attr]
            if all(run.metadata[attr] == value for run in self.runs):
                all_shared_attrs.add(attr)

        return all_shared_attrs

    # runs is a list of Runs
    # user_groups is a list of set(str), for example [{"ver", "hp"}, {"bfa"}]
    def run(self):
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

    def print_tree(self, root, indent=0):
        print(" " * indent + repr(root))

        if isinstance(root, Run):
            return

        for node in root.children:
            self.print_tree(node, indent + 2)
