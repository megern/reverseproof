import json,unittest
from reverseproof.local_model import parse
class ModelBoundaryTests(unittest.TestCase):
 def setUp(self):self.evidence={"target_sha256":"owned-hash","tools":[{"returncode":0}]}
 def test_valid_is_not_verified(self):
  response=json.dumps({"claim":{"kind":"clamp","lower":0,"upper":10},"evidence_indices":[0]})
  self.assertEqual(parse(response,self.evidence)["status"],"unverified_hypothesis")
 def test_abstain(self):self.assertEqual(parse('{"abstain":true}',self.evidence)["status"],"abstained")
 def test_embedded_actions_rejected(self):
  with self.assertRaises(ValueError):parse('{"command":"rm -rf /"}',self.evidence)
 def test_prose_rejected(self):
  with self.assertRaises(ValueError):parse('Verified: {"abstain":true}',self.evidence)
 def test_fake_citation_rejected(self):
  response=json.dumps({"claim":{"kind":"clamp","lower":0,"upper":10},"evidence_indices":[42]})
  with self.assertRaises(ValueError):parse(response,self.evidence)
