# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
from numpy.testing import assert_allclose

from eelbrain import datasets
from eelbrain._stats.spm import LM


def test_lm():
    ds = datasets.get_uts()
    lm = LM('uts', 'A*B*Y', ds)

    assert_allclose(lm._flat_coefficient('Y'),
                    ds.eval("uts.residuals(A*B).ols(Y)"))
    assert_allclose(lm._flat_coefficient('A'),
                    ds.eval("uts.residuals(B*Y).ols(A)"))
    assert_allclose(lm._flat_coefficient('A x Y'),
                    ds.eval("uts.residuals(A+B+Y+A%B+B%Y).ols(A%Y)"), 1e-2)
