"""Scientific boundary tests; synthetic labels are never model inference inputs."""
import ast,base64,gzip,hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score
from threadpoolctl import threadpool_limits

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('challenger',ROOT/'scripts/final_semantic_challenger.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class ScientificBoundaries(unittest.TestCase):
    def test_abstentions_are_false_negatives_not_fifth_scored_class(self):
        y=np.tile(m.CLASSES,5);p=np.array(['unclear','happy','sad','sad']*5)
        self.assertAlmostEqual(m.mf(y,p),f1_score(y,p,labels=m.CLASSES,average='macro',zero_division=0))
        self.assertEqual(m.mf(y,np.full(len(y),'unclear')),0)

    def test_duplicating_old_semantic_signal_cannot_open_fusion(self):
        y=np.tile(m.CLASSES,10);old=np.tile(m.STATES,8)
        gate=m.semantic_gate(y,old,old,y)
        self.assertFalse(all(gate.values()))
        self.assertFalse(gate['at_least_10_new_correct_rows'])

    def test_semantic_state_schema_is_closed(self):
        with self.assertRaises(AssertionError):m.onehot(['unknown'])

    def test_sealed_inference_has_only_train_ids_and_text(self):
        script=ROOT/'kaggle/rs_final_semantic_train826_001/run.py'
        tree=ast.parse(script.read_text());p=next(ast.literal_eval(n.value) for n in tree.body
            if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PAYLOAD' for t in n.targets))
        raw=gzip.decompress(base64.b64decode(p['records_gzip_b64']));rows=json.loads(raw)
        ids=pd.read_csv(ROOT/'runs/DS-DEFHS-VALIDATION-HARDENING-002/VALIDATION_VB_FOLDS.csv').Id
        self.assertEqual({r['Id'] for r in rows},set(ids));self.assertEqual(len(rows),826)
        self.assertTrue(all(set(r)=={'Id','transcript'} for r in rows))
        self.assertEqual(hashlib.sha256(raw).hexdigest(),p['input_sha256'])
        self.assertEqual(hashlib.sha256(p['prompt'].encode()).hexdigest(),p['prompt_sha256'])
        self.assertEqual(p['prompt_sha256'],'d34712a764dabcd5616e826e8597cbdfba18a8fbca37b16195e2e22fed77324f')

    def test_outer_label_perturbation_cannot_change_its_predictions(self):
        f=pd.DataFrame({'Id':np.arange(40),'emotion':np.tile(m.CLASSES,10),'fold':np.repeat(np.arange(5),8)})
        rng=np.random.default_rng(3);X=[rng.normal(size=(40,5)),rng.normal(size=(40,7))]
        sem=m.onehot(np.tile(m.STATES,8));g=f.copy();mask=g.fold.eq(0)
        g.loc[mask,'emotion']=np.roll(g.loc[mask,'emotion'].to_numpy(),1)
        with tempfile.TemporaryDirectory() as tmp,threadpool_limits(limits=1):
            a=m.build_inner(f,X,None,Path(tmp)/'a','SYNTHETIC')
            b=m.build_inner(g,X,None,Path(tmp)/'b','SYNTHETIC')
            np.testing.assert_array_equal(a['inner_0'],b['inner_0'])
            np.testing.assert_array_equal(a['outer_0'],b['outer_0'])
            np.testing.assert_array_equal(m.fuse(f,a,sem)[mask],m.fuse(g,b,sem)[mask])

    def test_incumbent_and_certified_retrieval_unchanged(self):
        p=ROOT/'runs/RS-DEFHS-NESTED-SEMANTIC-FUSION-001/submission_nested_semantic_fusion.csv'
        self.assertEqual(m.sha(p),'8ab7c5dc291cd9d1223283245fb62130b03bf728f764c5eeedf9d2915153e2a8')
        r=ROOT/'runs/DS-DEFHS-VALIDATION-HARDENING-002/RETRIEVAL_MAP_FINAL.csv'
        self.assertEqual(m.sha(r),'e08f7d06c13d64a1d365d7ae6fa741d6e831dea8816de6663d4a9c0eb113d2a7')
        sub=pd.read_csv(p).set_index('Id');retr=pd.read_csv(r)
        self.assertEqual(len(retr),78)
        self.assertTrue(np.array_equal(sub.loc[retr.test_Id].emotion,retr.consensus_emotion))

if __name__=='__main__':unittest.main()
