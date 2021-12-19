import collections

# inspo from
# https://stackoverflow.com/questions/6027558/flatten-nested-dictionaries-compressing-keys


def flatten(dictionary, parent_key=''):
    items = []
    for k, v in dictionary.items():
        new_key = parent_key + '_' + k if parent_key else k
        if isinstance(v, collections.abc.MutableMapping):
            items.extend(flatten(v, parent_key=new_key).items())
        else:
            items.append((new_key, v))
    return dict(items)
