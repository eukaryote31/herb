import os
import unittest
import tempfile
import filecmp
import math
import shutil

import herb.models as mod
import herb.metadata as meta
import herb.sync as sync
import herb.traversal as traversal
import time
from pathlib import Path


def touch(fpath):
    Path(fpath).touch()


def mkdir(dpath):
    try:
        os.mkdir(dpath)
    except FileExistsError:
        pass


def list_files(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print('{}{}'.format(subindent, f))


def dirs_identical(a, b):
    for af in traversal.traverse(a):
        relpath = traversal.rel_path_of(a, af)
        bf = os.path.join(b, relpath)

        if os.path.isdir(af):
            # TODO: check that directory stat is equal too
            continue
        else:
            if not filecmp.cmp(af, bf):
                return False

    return True


class TestSync(unittest.TestCase):
    def test_file_sync(self):

        meta_dir = tempfile.TemporaryDirectory()
        meta.init_metadata(meta_dir.name)

        with meta.transaction_scope(meta.Session()) as session:
            d1 = mod.Device(uuid='dev1', capacity=999999)
            d2 = mod.Device(uuid='dev2', capacity=999999)
            meta.add_device(session, d1)
            meta.add_device(session, d2)

        src_dir = tempfile.TemporaryDirectory()
        dest_dir = tempfile.TemporaryDirectory()
        dest_dir2 = tempfile.TemporaryDirectory()

        mkdir(src_dir.name + '/dir1')
        mkdir(src_dir.name + '/dir2')
        mkdir(src_dir.name + '/dir3')
        mkdir(src_dir.name + '/dir1/dir4')

        touch(src_dir.name + '/file1')
        touch(src_dir.name + '/dir1/file2')
        touch(src_dir.name + '/dir1/file3')
        touch(src_dir.name + '/dir2/file4')
        touch(src_dir.name + '/dir1/dir4/file5')

        res = sync.copy_tree(src_dir.name, dest_dir.name, 'dev1')

        self.assertTrue(dirs_identical(src_dir.name, dest_dir.name))
        # 4 dirs, 5 files
        self.assertEqual(res['updated'], 9)

        shutil.copy(meta_dir.name + '/metadata.db', '.')

        # simulate seperate session
        time.sleep(0.5)

        touch(src_dir.name + '/dir2/file4')
        touch(src_dir.name + '/dir1/dir4/file5')
        print('ffd')
        res = sync.copy_tree(src_dir.name, dest_dir.name, 'dev1')
        self.assertTrue(dirs_identical(src_dir.name, dest_dir.name))
        self.assertEqual(res['updated'], 4)

        res = sync.copy_tree(src_dir.name, dest_dir2.name, 'dev2')
        self.assertTrue(dirs_identical(src_dir.name, dest_dir2.name))

        meta_dir.cleanup()
        src_dir.cleanup()
        dest_dir.cleanup()