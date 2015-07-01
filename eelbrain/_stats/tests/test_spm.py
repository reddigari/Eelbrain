# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
from nose.tools import eq_
import numpy as np
from numpy.testing import assert_allclose

from eelbrain import datasets
from eelbrain._stats.spm import LM, RandomLM


def test_lm():
    ds = datasets.get_uts()
    lm = LM('uts', 'A*B*Y', ds)

    assert_allclose(lm._flat_coefficient('Y'),
                    ds.eval("uts.residuals(A*B).ols(Y)"))
    assert_allclose(lm._flat_coefficient('A'),
                    ds.eval("uts.residuals(B*Y).ols(A)"))
    assert_allclose(lm._flat_coefficient('A x Y'),
                    ds.eval("uts.residuals(A+B+Y+A%B+B%Y).ols(A%Y)"), 1e-2)


def test_random_lm():
    ds = datasets.get_uts()
    lms = []
    for i in xrange(5):
        ds['uts'].x += np.random.normal(0, 2, ds['uts'].shape)
        lms.append(LM('uts', 'A*B*Y', ds))
    rlm = RandomLM(lms)
    res = rlm.column_ttest('A x B', samples=100, pmin=0.05, mintime=0.025)
    eq_(res.clusters.n_cases, 6)

