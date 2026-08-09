import importlib.util,sys,unittest
from pathlib import Path
SCRIPT=Path(__file__).resolve().parents[1]/"scripts"/"07_public_ai_policy_simulation.py"
SPEC=importlib.util.spec_from_file_location("public_ai",SCRIPT); M=importlib.util.module_from_spec(SPEC); sys.modules[SPEC.name]=M; SPEC.loader.exec_module(M)
class PublicAITests(unittest.TestCase):
    def test_reproducible(self):
        a,_,_=M.simulate(3,M.POLICIES[4],n=250,periods=3); b,_,_=M.simulate(3,M.POLICIES[4],n=250,periods=3); self.assertEqual(a,b)
    def test_budget(self):
        _,_,x=M.simulate(2,M.POLICIES[4],n=300,periods=4); self.assertAlmostEqual(x["budget_error"],0,places=10)
    def test_all_metrics_finite(self):
        r,_,_=M.simulate(1,M.POLICIES[0],n=300,periods=3)
        for k,v in r.items():
            if k.startswith(("initial_","final_","delta_")): self.assertTrue(M.np.isfinite(v),k)
    def test_atkinson_zero_for_equal_income(self):
        s=M.population(1,100); income=M.np.ones(100)
        out=M.metrics(s,income,M.np.ones(100),income)
        self.assertAlmostEqual(out["atkinson_e1"],0,places=12)
if __name__=="__main__": unittest.main()
