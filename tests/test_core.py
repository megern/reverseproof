import unittest,tempfile,subprocess
from pathlib import Path
from reverseproof.core import digest,inventory,verify_owned,check_proposal
class EvidenceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.binary=Path(cls.tmp.name)/"clamp"
  subprocess.run(["/Library/Developer/CommandLineTools/usr/bin/clang","-isysroot","/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk","fixtures/clamp.c","-o",str(cls.binary)],check=True)
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_supported_and_refuted(self):
  claim={"kind":"clamp","lower":0,"upper":10}
  self.assertEqual(verify_owned(self.binary,claim,range(-5,16),digest(self.binary))["status"],"supported_on_tested_inputs")
  claim["upper"]=9
  self.assertTrue(verify_owned(self.binary,claim,[10],digest(self.binary))["counterexamples"])
 def test_approval_hash(self):
  with self.assertRaises(ValueError):verify_owned(self.binary,{},[1],"fake")
 def test_injection_schema(self):
  with self.assertRaises(ValueError):verify_owned(self.binary,{"kind":"shell","command":"echo hacked"},[1],digest(self.binary))
 def test_evidence_binding(self):
  evidence=inventory(self.binary)
  proposal={"claim":{"kind":"clamp","lower":0,"upper":10},"target_sha256":digest(self.binary),"evidence_indices":[0]}
  self.assertEqual(check_proposal(proposal,evidence)["status"],"unverified_hypothesis")
  proposal["target_sha256"]="fake"
  with self.assertRaises(ValueError):check_proposal(proposal,evidence)
 def test_empty_cases(self):
  with self.assertRaises(ValueError):verify_owned(self.binary,{},[],digest(self.binary))
