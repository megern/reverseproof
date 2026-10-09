import argparse,json
from pathlib import Path
from .core import inventory, verify_owned

def main():
 p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="command",required=True)
 s=sub.add_parser("inspect");s.add_argument("target",type=Path)
 s=sub.add_parser("verify-owned");s.add_argument("target",type=Path);s.add_argument("--approved-sha256",required=True);s.add_argument("--upper",type=int,default=10)
 a=p.parse_args()
 result=inventory(a.target) if a.command=="inspect" else verify_owned(a.target,{"kind":"clamp","lower":0,"upper":a.upper},range(-5,16),a.approved_sha256)
 print(json.dumps(result,indent=2))
if __name__=="__main__":main()
