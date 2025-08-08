import numpy as np
import pytest
from emlinefit.emlinefit import emlinefit
import os

parent_directory = os.path.abspath(os.path.join(os.getcwd(), os.pardir))

def test_plot():
  """
  Test plotting functionality.
  """

  wavelength=np.genfromtxt(parent_directory + '/emlinefit/data/wavelength_sample.txt')
  flux=np.genfromtxt(parent_directory + '/emlinefit/data/flux_sample.txt')
  
  emline=emlinefit(wavelength, flux, 1620, 1640, fit_type='asymmetric')
  emline.return_result()
  emline.plot_fit()

test_plot()