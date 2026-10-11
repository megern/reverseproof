import hashlib, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from reverseproof.core import digest

class DigestTests(unittest.TestCase):
    def test_multichunk_without_whole_file_read(self):
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory)/"weights"; payload=b"abcd"*600000
            target.write_bytes(payload)
            with patch.object(Path,"read_bytes",side_effect=AssertionError("whole file read")):
                self.assertEqual(digest(target),hashlib.sha256(payload).hexdigest())
