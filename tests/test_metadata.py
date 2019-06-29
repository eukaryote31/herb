import unittest
import tempfile

import herb.models as mod
import herb.metadata as meta


class TestMetadata(unittest.TestCase):
    def test_file_outdating(self):
        dir = tempfile.TemporaryDirectory()
        meta.init_metadata(dir.name)

        with meta.transaction_scope(meta.Session()) as session:
            d1 = mod.Device(uuid='dev1', capacity=999999)
            d2 = mod.Device(uuid='dev2', capacity=999999)

            self.assertIsNone(meta.file_latest(session, 'f1'))

            meta.add_device(session, d1)
            meta.add_device(session, d2)

            f1 = mod.File(path='f1', last_modified=0, device=d1, size=1, outdated=False)

            meta.add_file(session, f1)
            self.assertEqual(meta.file_latest(session, 'f1').last_modified, 0)

            f2 = mod.File(path='f1', last_modified=1, device=d1, size=1, outdated=False)
            meta.add_file(session, f2)
            self.assertEqual(meta.file_latest(session, 'f1').last_modified, 1)

            self.assertEqual(meta.outdated_files(session, 'dev1').count(), 0)
            f3 = mod.File(path='f1', last_modified=2, device=d2, size=1, outdated=False)
            meta.add_file(session, f3)
            self.assertEqual(meta.file_latest(session, 'f1').last_modified, 2)
            self.assertEqual(meta.outdated_files(session, 'dev1').count(), 1)
        dir.cleanup()