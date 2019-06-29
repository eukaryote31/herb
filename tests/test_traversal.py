import unittest
import tempfile

import herb.traversal as trav


class TestMetadata(unittest.TestCase):
    def test_traverse(self):
        # TODO: actual test case
        for f in trav.traverse('.'):
            pass

    def test_rel_path_of(self):
        self.assertEqual(trav.rel_path_of('/a/b/c', '/a/b/c/d/e'), 'd/e')
        self.assertEqual(trav.rel_path_of('/a/b/c/', '/a/b/c/d/e'), 'd/e')
        self.assertEqual(trav.rel_path_of('/a/b/../b/c/', '/a/b/c/d/e'), 'd/e')
        self.assertEqual(trav.rel_path_of('/a/b/../b/c/', '/a/../a/b/c/d/e'), 'd/e')

        self.assertEqual(trav.rel_path_of('/a/b/c', '/a/b/c/d/e/'), 'd/e')
        self.assertEqual(trav.rel_path_of('/a/b/../b/c/', '/a/../a/b/c/d/e/'), 'd/e')
