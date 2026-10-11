"""Check bounded verification reports without executing their target."""
import hashlib
import json
from pathlib import Path
import re
from .core import expected


def audit_report(path):
    path = Path(path)
    if path.stat().st_size > 16 * 1024 * 1024:
        raise ValueError('Verification report exceeds 16 MiB')
    raw = path.read_bytes()
    report = json.loads(raw)
    if not isinstance(report, dict) or not isinstance(report.get('target_sha256'), str) or not re.fullmatch(r'[0-9a-f]{64}', report['target_sha256']):
        raise ValueError('Invalid target digest')
    claim = report.get('claim')
    expected(claim, 0)
    cases = report.get('cases')
    if not isinstance(cases, list) or not 1 <= len(cases) <= 1000:
        raise ValueError('Expected between 1 and 1000 bounded cases')
    counters = []
    incomplete = 0
    for row in cases:
        if not isinstance(row, dict) or type(row.get('input')) is not int or abs(row['input']) > 1000000:
            raise ValueError('Invalid bounded input')
        if type(row.get('expected')) is not int or row['expected'] != expected(claim, row['input']):
            raise ValueError('Stored expected value disagrees with claim')
        actual = row.get('actual')
        if 'actual' not in row or ('returncode' in row and type(row['returncode']) is not int) or (
                'returncode' not in row and (not isinstance(row.get('error'), str) or not row['error'].strip())):
            raise ValueError('Incomplete process result fields')
        if actual is None:
            incomplete += 1
        elif type(actual) is not int or type(row.get('returncode')) is not int or row['returncode'] != 0:
            raise ValueError('Actual integer output requires a successful process exit')
        elif actual != row['expected']:
            counters.append(row)
    status = 'refuted' if counters else 'inconclusive' if incomplete else 'supported_on_tested_inputs'
    if report.get('status') != status or report.get('counterexamples') != counters:
        raise ValueError('Stored status or counterexamples disagree with cases')
    inputs = sorted({row['input'] for row in cases})
    return {'status': 'internally_consistent', 'verification_status': status,
            'report_sha256': hashlib.sha256(raw).hexdigest(), 'target_sha256': report['target_sha256'],
            'case_count': len(cases), 'distinct_inputs': len(inputs), 'incomplete_cases': incomplete,
            'counterexample_count': len(counters), 'tested_input_range': [inputs[0], inputs[-1]],
            'coverage': {'below_lower': any(x < claim['lower'] for x in inputs),
                         'inside_bounds': any(claim['lower'] <= x <= claim['upper'] for x in inputs),
                         'above_upper': any(x > claim['upper'] for x in inputs)},
            'scope': 'Internal consistency of stored finite-test evidence only. No target execution, report authenticity, universal equivalence or recovered-source claim.'}
