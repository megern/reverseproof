"""Escaped static report: target/model text is never executable HTML."""
import argparse,html,json
from pathlib import Path

def render(studies,output):
 sections=[]
 for study in studies:
  rows=[];summary=json.loads((study/"summary.json").read_text())
  for r in summary["results"]:
   fixture=r["fixture"]["id"];model=json.loads((study/(fixture+"-model.json")).read_text())
   status=r.get("verification",{}).get("status",r["model_response_status"])
   counter=r.get("verification",{}).get("counterexamples",[])
   values=[fixture,status,model["raw_response"],str(len(counter))]
   rows.append("<tr>"+"".join("<td><pre>"+html.escape(v)+"</pre></td>" for v in values)+"</tr>")
  sections.append("<h2>"+html.escape(study.name)+"</h2><table><tr><th>Owned fixture</th><th>Outcome</th><th>Raw model proposal</th><th>Counterexamples</th></tr>"+"".join(rows)+"</table>")
 document='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><meta http-equiv="Content-Security-Policy" content="default-src &apos;none&apos;; style-src &apos;unsafe-inline&apos;"><title>ReverseProof local study</title><style>body{font:16px system-ui;margin:32px;max-width:1200px;background:#111827;color:#e5e7eb}table{border-collapse:collapse;width:100%}td,th{padding:12px;border:1px solid #374151;text-align:left}pre{white-space:pre-wrap;overflow-wrap:anywhere}h1{color:#93c5fd}</style><h1>ReverseProof: evidence before confidence</h1><p>Offline original BF16 Qwen3-0.6B; four related owned ARM64 fixtures per prompt. No correct model interpretation demonstrated. Post-run development rounds, not independent held-out benchmarks.</p>'+''.join(sections)+'<p>Rejecting invalid answers and refuting wrong hypotheses is verifier behavior, not improved model accuracy. No general application reconstruction or injection-resistance claim.</p></html>'
 output.write_text(document)
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--studies",nargs="+",type=Path,required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args();render(a.studies,a.output)
