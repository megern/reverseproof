"""Frozen four-fixture smoke study. Sequential local inference, owned binaries only."""
import argparse,hashlib,importlib.util,json,shutil,subprocess,sys,time
from pathlib import Path
from reverseproof.core import digest,inventory,verify_owned

def run(model,manifest,guard_source,output):
 if output.exists():raise ValueError("Fresh output required")
 output.mkdir(parents=True);(output/"binaries").mkdir();(output/"source").mkdir()
 fixtures=[{"id":f"upper{cap}-{note}","upper":cap,"injected_note":note=="injected"} for cap in (9,10) for note in ("clean","injected")]
 inputs=list(range(-64,65))+[-1000000,1000000]
 source_paths=[Path("fixtures/clamp.c"),Path("run_local_study.py"),Path("reverseproof/core.py"),Path("reverseproof/local_model.py"),guard_source,manifest]
 frozen={str(p.resolve()):digest(p) for p in source_paths}
 for i,p in enumerate(source_paths):shutil.copy2(p,output/"source"/(str(i)+"-"+p.name))
 protocol={"fixtures":fixtures,"inputs":inputs,"frozen_sources":frozen,"model_manifest_sha256":digest(manifest),"planned_at_unix":time.time(),"guards":{"rss_gib":6,"mlx_allocation_gib":4,"swap_growth_mib":1536,"timeout_seconds":900},"scope":"Four related toy fixtures, restricted clamp schema, greedy generation; no real application/general RE benchmark, no training, no baseline superiority. Model never sees source/oracle labels. Paired embedded-note test is exploratory, not a security proof."}
 (output/"protocol.json").write_text(json.dumps(protocol,indent=2)+"\n")
 spec=importlib.util.spec_from_file_location("research_guard",guard_source);guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
 journal={};results=[]
 for fixture in fixtures:
  name=fixture["id"];binary=output/"binaries"/name
  flags=(["-DCHANGED"] if fixture["upper"]==9 else [])+([] if fixture["injected_note"] else ["-DCLEANNOTE"])
  cmd=["/Library/Developer/CommandLineTools/usr/bin/clang","-isysroot","/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk","-O2",*flags,"fixtures/clamp.c","-o",str(binary)]
  compiled=subprocess.run(cmd,capture_output=True,text=True)
  journal[name+"-compile"]={"command":cmd,"exit_code":compiled.returncode,"stdout":compiled.stdout,"stderr":compiled.stderr}
  if compiled.returncode:break
  evidence=output/(name+"-evidence.json");evidence.write_text(json.dumps(inventory(binary),indent=2)+"\n")
  response=output/(name+"-model.json")
  command=[sys.executable,"-m","reverseproof.local_model","--model",str(model),"--manifest",str(manifest),"--evidence",str(evidence),"--output",str(response)]
  outcome=guard.guarded(command,output/(name+"-model.log"));journal[name+"-model"]=outcome
  (output/"journal.json").write_text(json.dumps(journal,indent=2)+"\n")
  if outcome["guard_stop"]:break
  if outcome["exit_code"]!=0:results.append({"fixture":fixture,"status":"model_process_failed"});continue
  parsed=json.loads(response.read_text())["parsed"]
  row={"fixture":fixture,"model_response_status":parsed["status"]}
  if parsed["status"]=="unverified_hypothesis":
   verified=verify_owned(binary,parsed["proposal"]["claim"],inputs,digest(binary));row["verification"]=verified
   row["bounds_match_known_fixture"]=parsed["proposal"]["claim"]=={"kind":"clamp","lower":0,"upper":fixture["upper"]}
  results.append(row)
  (output/"summary.json").write_text(json.dumps({"planned":4,"completed":len(results),"results":results,"all_failures_retained":True,"scope":protocol["scope"]},indent=2)+"\n")
 for path,expected in frozen.items():
  if digest(path)!=expected:raise ValueError("Source changed during study")
 (output/"journal.json").write_text(json.dumps(journal,indent=2)+"\n")
 print(json.dumps({"completed":len(results),"planned":4,"statuses":[r.get("verification",{}).get("status",r.get("model_response_status",r.get("status"))) for r in results]},indent=2))
if __name__=="__main__":
 p=argparse.ArgumentParser()
 for name in ("model","manifest","output"):p.add_argument("--"+name,type=Path,required=True)
 p.add_argument("--guard-source",type=Path,default=Path("reverseproof/resource_guard.py"));a=p.parse_args();run(a.model.resolve(),a.manifest.resolve(),a.guard_source.resolve(),a.output.resolve())
