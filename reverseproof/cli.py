"""Local inspection and explicitly approved bounded verification."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from .core import inventory, verify_owned
from .patterns import propose


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,help='Save JSON to a fresh path; existing reports are preserved')
    sub=parser.add_subparsers(dest='command',required=True)
    for command in ('inspect','propose-pattern'):
        sub.add_parser(command).add_argument('target',type=Path)
    verification=sub.add_parser('verify-owned')
    verification.add_argument('target',type=Path)
    verification.add_argument('--approved-sha256',required=True)
    verification.add_argument('--lower',type=int,default=0)
    verification.add_argument('--upper',type=int,default=10)
    verification.add_argument('--min-input',type=int,default=-5)
    verification.add_argument('--max-input',type=int,default=15)
    args=parser.parse_args(argv)
    try:
        if args.output and (args.output.exists() or args.output.resolve()==args.target.resolve()):
            raise ValueError('Output must be a fresh path distinct from the target')
        if args.command=='inspect': result=inventory(args.target)
        elif args.command=='propose-pattern':result=propose(inventory(args.target))
        else:
            if not 0<=args.max_input-args.min_input<1000:
                raise ValueError('Input range must contain between 1 and 1000 integers')
            result=verify_owned(args.target,{'kind':'clamp','lower':args.lower,'upper':args.upper},
                                range(args.min_input,args.max_input+1),args.approved_sha256)
        serialized=json.dumps(result,indent=2)+'\n'
        if args.output:
            args.output.parent.mkdir(parents=True,exist_ok=True)
            with args.output.open('x') as stream:stream.write(serialized)
            print(str(args.output))
        else:print(serialized,end='')
        return 1 if result.get('status')=='refuted' else 0
    except (ValueError,OSError,subprocess.SubprocessError) as error:
        print(f'Local analysis failed: {error}',file=sys.stderr)
        return 2

if __name__=='__main__':sys.exit(main())
