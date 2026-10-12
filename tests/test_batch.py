from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from reverseproof.batch import inspect_batch
class BatchTests(unittest.TestCase):
    def test_partial_errors_are_preserved_without_target_execution(self):
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp)/'fixture';target.write_bytes(b'owned fixture')
            with patch('reverseproof.batch.inventory',return_value={'tools':[{'returncode':1}],'target_sha256':'a'*64}) as inventory:
                report=inspect_batch([target,Path(temp)/'missing'])
            self.assertEqual([row['status'] for row in report['results']],['static_tool_error','error']);inventory.assert_called_once()
    def test_duplicate_paths_are_rejected(self):
        with self.assertRaises(ValueError):inspect_batch(['a','a'])
