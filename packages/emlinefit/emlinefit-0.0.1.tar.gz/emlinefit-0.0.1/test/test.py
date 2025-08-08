import numpy as np
import pytest
from emlinefit.emlinefit import emlinefit
import os

parent_directory = os.path.abspath(os.path.join(os.getcwd(), os.pardir))

def test_fit_asym_line():
  """
  Test the fitting of an asymmetric line.
  """
  wavelength=np.genfromtxt(os.path.join(parent_directory, 'data/wavelength_sample.txt'))
  flux=np.genfromtxt(os.path.join(parent_directory, 'data/flux_sample.txt'))

  emline=emlinefit(wavelength, flux, 1620, 1640, fit_type='asymmetric')
  A, asym, d, width, cov = emline.return_result()

  ind = (wavelength>1620) & (wavelength<1640)
  A_exp = np.max(flux[ind])
  asym_exp = 0.1
  d_exp = 0.4

  assert A == pytest.approx(A_exp, abs = 10 * A_exp)
  assert asym == pytest.approx(asym_exp, abs = 1)
  assert d == pytest.approx(d_exp, abs = 1)
  
  print('Asymmetric Gaussian fitting tested successfully.')
  return(A, asym, d, width, cov)

test_fit_asym_line()