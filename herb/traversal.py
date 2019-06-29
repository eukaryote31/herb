import os
from pathlib import Path

from more_itertools import unique_everseen


def traverse(root: str):
    priority = []
    ignore = []
    priority_file = os.path.join(root, '.backup_priority')
    ignore_file = os.path.join(root, '.backup_ignore')

    did_include_all = False
    if os.path.isfile(priority_file):
        with open(priority_file) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                if line == '*':
                    did_include_all = True
                priority.extend(Path(root).glob(line))

    if not did_include_all:
        priority.extend(Path(root).glob('*'))

    if os.path.isfile(ignore_file):
        with open(ignore_file) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                ignore.append(line)

    to_trav = [x for x in unique_everseen(priority) if x not in ignore]

    for f in to_trav:
        yield f
        if os.path.isdir(f):
            for ret in traverse(f):
                yield ret


def rel_path_of(root: str, path: str):
    root = os.path.abspath(root)
    path = os.path.abspath(path)
    if not root.endswith(os.path.sep):
        root += os.path.sep

    assert path.startswith(root)

    return path[len(root):]
