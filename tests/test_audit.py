import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from reverseproof.audit import audit_report


class ReportAuditTests(unittest.TestCase):
    def report(self):
        return {'target_sha256': 'a' * 64, 'claim': {'kind': 'clamp', 'lower': 0, 'upper': 10},
                'status': 'supported_on_tested_inputs', 'counterexamples': [],
                'cases': [{'input': -1, 'expected': 0, 'actual': 0, 'returncode': 0},
                          {'input': 5, 'expected': 5, 'actual': 5, 'returncode': 0},
                          {'input': 11, 'expected': 10, 'actual': 10, 'returncode': 0}]}

    def check(self, report):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'report.json'
            path.write_text(json.dumps(report))
            return audit_report(path)

    def test_coverage_audited_without_execution(self):
        with patch('subprocess.run', side_effect=AssertionError('Must not execute')):
            result = self.check(self.report())
        self.assertEqual(result['verification_status'], 'supported_on_tested_inputs')
        self.assertTrue(all(result['coverage'].values()))

    def test_tampered_expected_status_and_counterexamples_rejected(self):
        for mutation in ('expected', 'status', 'counterexamples'):
            report = self.report()
            if mutation == 'expected': report['cases'][0]['expected'] = 1
            elif mutation == 'status': report['status'] = 'refuted'
            else: report['counterexamples'] = [report['cases'][0]]
            with self.assertRaises(ValueError): self.check(report)

    def test_refutation_and_incomplete_cases_remain_distinct(self):
        report = self.report();report['cases'][0]['actual'] = 1
        report['counterexamples'] = [copy.deepcopy(report['cases'][0])];report['status'] = 'refuted'
        self.assertEqual(self.check(report)['counterexample_count'], 1)
        report = self.report();report['cases'][0]['actual'] = None;report['status'] = 'inconclusive'
        self.assertEqual(self.check(report)['incomplete_cases'], 1)

    def test_boolean_actual_rejected(self):
        report = self.report();report['cases'][0]['actual'] = False
        with self.assertRaises(ValueError): self.check(report)
