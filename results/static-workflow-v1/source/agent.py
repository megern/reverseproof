"""Fixed local workflow: inspect, propose, validate, optionally verify an owned target."""
import argparse,json,sys,shutil
from pathlib import Path
from .core import digest,inventory,verify_owned,check_proposal
from .patterns import propose

def finish(evidence,model_result,target,approved_sha256):
 """Model and rule provenance stay distinct; no model selects an executable/tool."""
 parsed=model_result.get('parsed',{'status':'model_not_available'})
 if parsed['status']=='unverified_hypothesis':hypothesis=check_proposal(parsed['proposal'],evidence);method='local_model'
 else:hypothesis=propose(evidence);method='exact_instruction_rule_fallback'
 result={'target_sha256':evidence['target_sha256'],'local_model_status':parsed['status'],'hypothesis_method':method,'hypothesis':hypothesis,'status':'unverified_hypothesis' if hypothesis['status']=='unverified_hypothesis' else 'abstained'}
 if hypothesis['status']=='unverified_hypothesis' and approved_sha256 is not None:
  if evidence['target_sha256']!=approved_sha256:raise ValueError('Owned execution approval does not match evidence')
  result['verification']=verify_owned(target,hypothesis['proposal']['claim'],list(range(-64,65))+[-1000000,1000000],approved_sha256)
  result['status']=result['verification']['status']
 result['scope']='Fixed workflow, not a self-directed tool loop. Model and rule outcomes are distinguished. Finite input support is not universal equivalence. Owned digest approval is not OS isolation.'
 return result

def run(target,model,manifest,output,approved_sha256=None):
 if output.exists():raise ValueError('Fresh output required')
 evidence=inventory(target)
 if approved_sha256 is not None and evidence['target_sha256']!=approved_sha256:raise ValueError('Owned execution approval hash mismatch')
 output.mkdir(parents=True);evidence_path=output/'evidence.json';evidence_path.write_text(json.dumps(evidence,indent=2)+'\n')
 protocol={'target_sha256':evidence['target_sha256'],'owned_execution_approved':approved_sha256 is not None,'model_manifest_sha256':digest(manifest),'fixed_inputs':list(range(-64,65))+[-1000000,1000000],'frozen_workflow_sha256':{str(p):digest(p) for p in (Path(__file__),Path(__file__).with_name('core.py'),Path(__file__).with_name('local_model.py'),Path(__file__).with_name('patterns.py'),Path(__file__).with_name('resource_guard.py'))},'fallback':'Use a narrow exact-instruction rule only when model schema is invalid or model abstains. Preserve valid-but-refuted model proposals without replacing them with a favorable rule result.'}
 (output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
 (output/'source').mkdir()
 for original in protocol['frozen_workflow_sha256']:shutil.copy2(original,output/'source'/Path(original).name)
 from .resource_guard import guarded
 response=output/'model.json'
 command=[sys.executable,'-m','reverseproof.local_model','--model',str(model),'--manifest',str(manifest),'--evidence',str(evidence_path),'--output',str(response)]
 outcome=guarded(command,output/'model.log');(output/'resource-outcome.json').write_text(json.dumps(outcome,indent=2)+'\n')
 if outcome['guard_stop'] or outcome['exit_code']!=0:
  result={'status':'stopped','resource_outcome':outcome,'scope':'No interpretation or execution after a model process failure/resource stop'}
 else:result=finish(evidence,json.loads(response.read_text()),target,approved_sha256)
 (output/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'hypothesis_method':result.get('hypothesis_method'),'counterexample_count':len(result.get('verification',{}).get('counterexamples',[])),'full_report':str(output/'report.json')},indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('target','model','output'):p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--manifest',type=Path,default=Path('models/qwen3-0.6b-original.json'));p.add_argument('--owned-sha256',help='Explicit execution approval for an owned trusted fixture only')
 a=p.parse_args();run(a.target.resolve(),a.model.resolve(),a.manifest.resolve(),a.output.resolve(),a.owned_sha256)
