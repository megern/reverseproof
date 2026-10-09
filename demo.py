"""Build and run only our own tiny fixture, never downloaded applications."""
import json,subprocess
from pathlib import Path
from reverseproof.core import digest,inventory,verify_owned
out=Path("results");out.mkdir(exist_ok=True);build=Path("build");build.mkdir(exist_ok=True)
reports=[]
for name,flags in [("original",[]),("changed",["-DCHANGED"])]:
 target=build/name
 subprocess.run(["/Library/Developer/CommandLineTools/usr/bin/clang","-isysroot","/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk","-O2",*flags,"fixtures/clamp.c","-o",str(target)],check=True)
 reports.append({"variant":name,"evidence":inventory(target),"verification":verify_owned(target,{"kind":"clamp","lower":0,"upper":10},range(-5,16),digest(target))})
(out/"demo.json").write_text(json.dumps({"protocol":"Fixed inputs -5..15; clamp [0,10] hypothesis; owned C fixture only","results":reports},indent=2)+"\n")
print([(r["variant"],r["verification"]["status"]) for r in reports])
