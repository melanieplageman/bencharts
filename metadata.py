from collections.abc import Mapping

class RunMetadata(Mapping):
    def __init__(self, metadata):
        self.metadata = metadata

    def __getitem__(self, key):
        return self.metadata[key]

    def __iter__(self):
        return iter(self.metadata)

    def __len__(self):
        return len(self.metadata)

    def __eq__(self, other):
        return self.metadata == other.metadata

    def __hash__(self):
        return hash(frozenset(self.metadata.items()))

    def __repr__(self):
        return repr(self.metadata)

    def keys(self):
        return self.metadata.keys()

    def items(self):
        return self.metadata.items()

    def values(self):
        return self.metadata.values()

    # Given other, a RunMetadata, return a RunMetadata which includes all of
    # the contents of both with no duplicates
    def union(self, other):
        return RunMetadata(self.metadata | other.metadata)

    # Return a RunMetadata containing only the metadata in self that was not
    # exactly the same in other
    def minus(self, other):
        result = {}
        for k, v in self.metadata.items():
            if k in other.metadata and other.metadata[k] == v:
                continue
            result[k] = v
        return RunMetadata(result)

    def subset(self, chosen_keys):
        return RunMetadata({ k: v for k, v in self.metadata.items() if k in chosen_keys})

    def pretty_print(self):
        return ''.join([f' {k}: {v}' for k, v in self.metadata.items()]) + '\n'
