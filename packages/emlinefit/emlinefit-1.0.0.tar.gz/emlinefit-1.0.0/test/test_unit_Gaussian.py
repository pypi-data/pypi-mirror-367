import numpy as np
from emlinefit.emlinefit import emlinefit
import pytest

def test_unit_Gaussian():

    """
    Unit test for a purely Gaussian dataset
    """

    x = np.linspace(0, 100, 100)
    mu = 50
    sigma = 6
    amp = 8
    exponential = -1 * (x - mu)**2 / (2 * sigma**2)
    y = amp * np.exp(exponential)

    assert len(y) == len(x)

    fit = emlinefit(x, y, mu - 5, mu + 20, 'gaussian')
    a, b, c, d = fit.return_result()
    fit.plot_fit()

    assert a == pytest.approx(amp, abs=0.05*amp)
    assert b == pytest.approx(mu, abs=0.05*amp)
    assert c == pytest.approx(sigma, abs=0.05*amp)

    print(a,amp)
    print(b, mu)
    print(c, sigma)

test_unit_Gaussian()