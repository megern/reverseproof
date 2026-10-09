import json,unittest
from pathlib import Path
from unittest.mock import patch
from reverseproof.agent import finish
class WorkflowTests(unittest.TestCase):
 def setUp(self):self.evidence=json.loads(Path('results/demo.json').read_text())['results'][0]['evidence']
 def test_no_approval_never_executes(self):
  with patch('reverseproof.agent.verify_owned') as execute:
   r=finish(self.evidence,{'parsed':{'status':'rejected_response'}},Path('unused'),None)
   execute.assert_not_called();self.assertEqual(r['hypothesis_method'],'exact_instruction_rule_fallback');self.assertEqual(r['status'],'unverified_hypothesis')
 def test_valid_model_counterexample_never_becomes_favorable_fallback(self):
  model={'parsed':{'status':'unverified_hypothesis','proposal':{'claim':{'kind':'clamp','lower':0,'upper':777},'target_sha256':self.evidence['target_sha256'],'evidence_indices':[1]}}}
  with patch('reverseproof.agent.verify_owned',return_value={'status':'refuted','counterexamples':[{'input':10}]}) as execute:
   r=finish(self.evidence,model,Path('owned'),self.evidence['target_sha256'])
   self.assertEqual(r['hypothesis_method'],'local_model');self.assertEqual(r['status'],'refuted');self.assertEqual(execute.call_args.args[1]['upper'],777)
 def test_wrong_approval_rejected(self):
  with self.assertRaises(ValueError):finish(self.evidence,{'parsed':{'status':'abstained'}},Path('unused'),'wrong')
