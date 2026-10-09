"""Post-model development smoke test of an exact-signature baseline; no trained AI."""
import argparse,json,shutil,subprocess,time
from pathlib import Path
from reverseproof.core import digest,inventory,verify_owned
from reverseproof.patterns import propose

def run(output):
 if output.exists():raise ValueError("Fresh output required")
 output.mkdir(parents=True);(output/"binaries").mkdir();(output/"source").mkdir()
 fixtures=[("upper9-clean",["-DCHANGED","-DCLEANNOTE"],9),("upper9-injected",["-DCHANGED"],9),("upper10-clean",["-DCLEANNOTE"],10),("upper10-injected",[],10),("negative-affine",["-DAFFINE"],None)]
 sources=[Path("fixtures/clamp.c"),Path("reverseproof/patterns.py"),Path("reverseproof/core.py"),Path(__file__)]
 protocol={"planned_at_unix":time.time(),"fixtures":fixtures,"inputs":list(range(-64,65))+[-1000000,1000000],"source_sha256":{str(s):digest(s) for s in sources},"scope":"Post-run rule baseline developed from the same fixtures. Four related clamp examples and one affine negative, not source-separated test data, not general decompilation accuracy. No local-model inference in this study."}
 for i,s in enumerate(sources):shutil.copy2(s,output/"source"/(str(i)+"-"+s.name))
 (output/"protocol.json").write_text(json.dumps(protocol,indent=2)+"\n");rows=[]
 for name,flags,known_upper in fixtures:
  binary=output/"binaries"/name
  cmd=["/Library/Developer/CommandLineTools/usr/bin/clang","-isysroot","/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk","-O2",*flags,"fixtures/clamp.c","-o",str(binary)]
  r=subprocess.run(cmd,capture_output=True,text=True)
  if r.returncode:rows.append({"fixture":name,"compile_failed":r.stderr});continue
  evidence=inventory(binary);proposal=propose(evidence);row={"fixture":name,"evidence":evidence,"proposal":proposal,"known_upper":known_upper}
  if proposal["status"]=="unverified_hypothesis":row["verification"]=verify_owned(binary,proposal["proposal"]["claim"],protocol["inputs"],digest(binary))
  rows.append(row)
 summary={"results":rows,"planned":5,"completed":len(rows),"scope":protocol["scope"]}
 (output/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
 print([(r["fixture"],r.get("verification",{}).get("status",r.get("proposal",{}).get("status","compile_failed"))) for r in rows])
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True);run(p.parse_args().output.resolve())
