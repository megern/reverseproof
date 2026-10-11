"""Freeze and probe eight owned compiler variants; preserve abstentions."""
import argparse
import json
from pathlib import Path
import subprocess
import time
from reverseproof.core import digest, inventory, verify_owned
from reverseproof.patterns import propose


def run(output):
    root = Path(__file__).resolve().parent
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    binaries = output / 'binaries'; binaries.mkdir()
    source = root / 'fixtures/alternate_clamp.c'
    frozen = {str(path.relative_to(root)): digest(path) for path in
              (source, root/'reverseproof/patterns.py', root/'reverseproof/core.py', Path(__file__).resolve())}
    cells = [{'id': f'upper{upper}-{opt}', 'upper': upper, 'optimization': opt}
             for upper in (7, 23) for opt in ('O0', 'O1', 'O2', 'Os')]
    protocol = {'cells': cells, 'source_sha256': frozen, 'planned_at_unix': time.time(),
                'inputs': list(range(-64, 65)) + [-1000000, 1000000],
                'scope': 'Eight related owned synthetic variants. Frozen signature rules; abstentions retained. No LLM evaluation, real-app coverage or universal proof.'}
    (output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    results = []
    compiler = '/Library/Developer/CommandLineTools/usr/bin/clang'
    for cell in cells:
        binary = binaries/cell['id']
        command = [compiler, '-isysroot', '/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk',
                   '-'+cell['optimization'], '-DUPPER='+str(cell['upper']), str(source), '-o', str(binary)]
        subprocess.run(command, capture_output=True, text=True, check=True, timeout=30)
        evidence = inventory(binary)
        proposal = propose(evidence)
        verification = None
        if proposal['status'] != 'abstained':
            verification = verify_owned(binary, proposal['proposal']['claim'], protocol['inputs'], digest(binary))
        results.append({'cell': cell, 'target_sha256': digest(binary), 'proposal': proposal,
                        'verification': verification})
    if any(digest(root/name) != expected for name, expected in frozen.items()):
        raise ValueError('Frozen source changed during study')
    report = {'protocol_sha256': digest(output/'protocol.json'), 'results': results,
              'abstained': sum(row['proposal']['status']=='abstained' for row in results),
              'supported_on_tested_inputs': sum(row['verification'] is not None and row['verification']['status']=='supported_on_tested_inputs' for row in results),
              'scope': protocol['scope']}
    (output/'coverage.json').write_text(json.dumps(report, indent=2)+'\n')
    return report

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.output), indent=2))
