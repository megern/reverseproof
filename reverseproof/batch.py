"""Batch static hypotheses; no target binary execution or model-selected tools."""
import argparse
import json
from pathlib import Path
import subprocess
from .core import inventory
from .patterns import propose
from .report_bundle import write_bundle

def inspect_batch(paths):
    paths = [Path(path).resolve() for path in paths]
    if not 1 <= len(paths) <= 100 or len(set(paths)) != len(paths):
        raise ValueError('Supply 1..100 distinct target paths')
    results = []
    for path in paths:
        try:
            if not path.is_file() or path.stat().st_size > 64 * 1024 * 1024:
                raise ValueError('Target missing or exceeds 64 MiB')
            evidence = inventory(path)
            if any((row['returncode'] != 0 for row in evidence['tools'])):
                results.append({'target': str(path), 'status': 'static_tool_error', 'evidence': evidence})
            else:
                proposal=propose(evidence)
                results.append({'target': str(path), 'status': 'abstained' if proposal.get('status')=='abstained' else 'unverified_static_hypothesis', 'proposal': proposal, 'evidence': evidence})
        except (ValueError, OSError, subprocess.SubprocessError) as error:
            results.append({'target': str(path), 'status': 'error', 'error': str(error)})
    return {'tool': 'reverseproof-batch', 'target_count': len(paths), 'results': results, 'scope': 'Static tool outputs and rule proposals only; no target execution, behavioral verification, source recovery or safety claim.'}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('targets', nargs='+', type=Path)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    try:
        report = inspect_batch(a.targets)
        write_bundle(a.output, report, 'ReverseProof static batch review')
        print(json.dumps({'target_count': report['target_count']}))
        return 2 if any((row['status'] in ('error', 'static_tool_error') for row in report['results'])) else 0
    except (ValueError, OSError) as e:
        p.exit(2, str(e) + '\n')
if __name__ == '__main__':
    raise SystemExit(main())
