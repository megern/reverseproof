import contextlib,io,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from reverseproof.cli import main
class CliTests(unittest.TestCase):
    def test_no_overwrite_before_inspection(self):
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/'target';target.write_text('retain')
            with patch('reverseproof.cli.inventory') as inspect,contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main(['--output',str(target),'inspect',str(target)]),2)
                inspect.assert_not_called()
            self.assertEqual(target.read_text(),'retain')
    def test_invalid_range_before_execution(self):
        with patch('reverseproof.cli.verify_owned') as execute,contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(['verify-owned','target','--approved-sha256','fake','--min-input','10','--max-input','-10']),2)
            execute.assert_not_called()
    def test_refuted_cli_exit(self):
        with patch('reverseproof.cli.verify_owned',return_value={'status':'refuted'}),contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(['verify-owned','target','--approved-sha256','fake']),1)
