"""Meaningful boundary checks for the prospective nested experiment."""
import sys,unittest
from pathlib import Path
import numpy as np
from threadpoolctl import threadpool_limits
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import system_f_evaluate as S

class Boundaries(unittest.TestCase):
    def test_outer_labels_cannot_affect_own_expert_or_meta(self):
        rng=np.random.default_rng(774);fold=np.repeat(np.arange(5),24)
        y=np.tile(np.tile(S.L,6),5);ids=np.arange(len(y));X=rng.normal(size=(120,7))
        sem=rng.normal(size=(120,15));wave=rng.normal(size=(120,8))
        arrays={k:(wave.copy(),wave[fold==k]) for k in range(5)}
        y2=y.copy();y2[fold==0]=np.roll(y2[fold==0],1)
        with threadpool_limits(1):
            p,inn,_=S.nested_new(X,y,fold,ids);p2,inn2,_=S.nested_new(X,y2,fold,ids)
            np.testing.assert_array_equal(p[fold==0],p2[fold==0]);np.testing.assert_array_equal(inn[0],inn2[0])
            m=S.fuse(y,fold,arrays,sem,p,inn);m2=S.fuse(y2,fold,arrays,sem,p2,inn2)
        np.testing.assert_array_equal(m[fold==0],m2[fold==0])

    def test_null_added_features_reproduce_unchanged_meta(self):
        rng=np.random.default_rng(819);fold=np.repeat(np.arange(5),24);y=np.tile(np.tile(S.L,6),5)
        sem=rng.normal(size=(120,15));w=rng.normal(size=(120,8));arrays={k:(w,w[fold==k]) for k in range(5)}
        with threadpool_limits(1):
            a=S.fuse(y,fold,arrays,sem)
            b=S.fuse(y,fold,arrays,sem,np.zeros((120,4)),{k:np.zeros((120,4)) for k in range(5)})
        np.testing.assert_allclose(a,b,rtol=0,atol=1e-12)

if __name__=='__main__':unittest.main()
