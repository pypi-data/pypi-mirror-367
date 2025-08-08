# emlinefit
Emlinefit is a emission line fitting package that includes gaussian and asymmetric gaussian profiles.


## Installation Instructions
You can install emlinefit via pip:
```
pip install emlinefit
```

## Getting Started
Here is a quick tutorial that will help you start using emlinefit. This guide uses data available on [GitHub](https://github.com/laurenelicker/emlinefit/tree/main/emlinefit/data) and fits to a gaussian profile.

```
import emlinefit
import numpy as np

wave = np.genfromtxt("{}/data/wavelength_sample.txt")
flux = np.genfromtxt("{}/data/flux_sample.txt")

fit = emlinefit.emlinefit(wave, flux, 1625, 1635, fit_type = 'gaussian')
fit.return_result()
fit.plot_fit()
```

## Contributing
Let us know if you have any issues, questions, or suggestions but opening an [issue] (https://github.com/laurenelicker/emlinefit/issues).