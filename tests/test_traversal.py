import unittest
import tempfile

import herb.traversal as trav


class TestMetadata(unittest.TestCase):
    def test_traverse(self):
        # TODO: actual test case
        for f in trav.traverse('.'):
            pass
