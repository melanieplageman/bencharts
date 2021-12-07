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

    def shared_metadata(self, except_keys):
        return RunMetadata({ k: v for k, v in self.metadata.items() if k not in except_keys })

