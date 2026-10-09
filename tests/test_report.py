import json,tempfile,unittest
from pathlib import Path
from reverseproof.report import render
class ReportBoundaryTests(unittest.TestCase):
 def test_model_html_is_escaped(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);study=root/'study';study.mkdir()
   (study/'summary.json').write_text(json.dumps({'results':[{'fixture':{'id':'owned'},'model_response_status':'rejected_response'}]}))
   (study/'owned-model.json').write_text(json.dumps({'raw_response':'<script>alert(1)</script>'}))
   output=root/'report.html';render([study],output);text=output.read_text()
   self.assertNotIn('<script>',text);self.assertIn('&lt;script&gt;',text);self.assertIn('Content-Security-Policy',text)
