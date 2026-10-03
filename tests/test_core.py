import copy,json,subprocess,sys,tempfile,unittest
from pathlib import Path
from trustcheck.core import evaluate,run_suite,wildcard
from trustcheck.__main__ import read_json
ROOT=Path(__file__).resolve().parents[1]
P=json.loads((ROOT/'examples/restricted-policy.json').read_text())
S=json.loads((ROOT/'examples/scenarios.json').read_text())
class Tests(unittest.TestCase):
 def setUp(self): self.p=copy.deepcopy(P); self.c=dict(S['scenarios'][0]['claims'])
 def d(self): return evaluate(self.p,S['provider'],self.c)['decision']
 def test_allow(self): self.assertEqual(self.d(),'ALLOW')
 def test_branch(self):
  self.c['sub']=S['scenarios'][1]['claims']['sub']; self.assertEqual(self.d(),'DENY')
 def test_audience(self): self.c['aud']='wrong'; self.assertEqual(self.d(),'DENY')
 def test_deny_precedence(self):
  a=self.p['Statement'][0]; d=copy.deepcopy(a); d['Effect']='Deny'
  for seq in [[a,d],[d,a]]: self.p['Statement']=seq; self.assertEqual(self.d(),'DENY')
 def test_other_provider(self): self.assertEqual(evaluate(self.p,S['provider'].replace('123456789012','999999999999'),self.c)['decision'],'DENY')
 def test_or_values(self):
  self.p['Statement'][0]['Condition']['StringEquals']['token.actions.githubusercontent.com:aud']=['wrong','sts.amazonaws.com']; self.assertEqual(self.d(),'ALLOW')
 def test_unknown_deny(self): self.p['Statement'].append({'Effect':'Deny','NotPrincipal':'*'}); self.assertEqual(self.d(),'UNKNOWN')
 def test_unknown_operator(self):
  self.p['Statement'][0]['Condition']['IpAddress']={'aws:SourceIp':'1.2.3.4'}; self.assertEqual(self.d(),'UNKNOWN')
 def test_missing_claim(self): del self.c['aud']; self.assertEqual(self.d(),'UNKNOWN')
 def test_variables(self):
  self.p['Statement'][0]['Condition']['StringEquals']['token.actions.githubusercontent.com:sub']='${aws:username}'; self.assertEqual(self.d(),'UNKNOWN')
 def test_no_condition(self):
  del self.p['Statement'][0]['Condition']; self.c['aud']='wrong'; self.assertEqual(self.d(),'ALLOW')
 def test_empty_suite(self):
  with self.assertRaises(ValueError): run_suite(self.p,{'provider':S['provider'],'scenarios':[]})
 def test_duplicate_names(self):
  s=copy.deepcopy(S); s['scenarios'].append(s['scenarios'][0])
  with self.assertRaises(ValueError): run_suite(self.p,s)
 def test_wildcards(self):
  self.assertFalse(wildcard('[ab]','a')); self.assertTrue(wildcard('[ab]','[ab]')); self.assertTrue(wildcard('repo:*:?','repo:test:x')); self.assertFalse(wildcard('Prod','prod'))
 def test_duplicate_json(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'p.json'; p.write_text('{"Effect":"Deny","Effect":"Allow"}')
   with self.assertRaises(ValueError): read_json(p)
 def test_missing_action(self): del self.p['Statement'][0]['Action']; self.assertEqual(self.d(),'UNKNOWN')
 def test_broad_regression(self):
  p=json.loads((ROOT/'examples/broad-policy.json').read_text()); r=run_suite(p,S)
  self.assertEqual([x['name'] for x in r if x['status']=='FAIL'],['Feature branch','Pull request context'])
 def test_single_statement(self): self.p['Statement']=self.p['Statement'][0]; self.assertEqual(self.d(),'ALLOW')
 def test_cli_formats(self):
  for name,code in [('restricted-policy.json',0),('broad-policy.json',1)]:
   for fmt in ['text','json','markdown']:
    r=subprocess.run([sys.executable,'-m','trustcheck','--policy',str(ROOT/'examples'/name),'--scenarios',str(ROOT/'examples/scenarios.json'),'--format',fmt],capture_output=True,text=True,cwd=ROOT)
    self.assertEqual(r.returncode,code,r.stderr)
    if fmt=='json': self.assertEqual(len(json.loads(r.stdout)['results']),5)
 def test_cli_invalid(self):
  r=subprocess.run([sys.executable,'-m','trustcheck','--policy','missing','--scenarios','examples/scenarios.json'],capture_output=True,cwd=ROOT); self.assertEqual(r.returncode,2)
