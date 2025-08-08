## LensMC - Weak lensing shear measurement with forward modelling and MCMC sampling

LensMC is a Python package for weak lensing shear measurement specifically developed for Euclid and stage-IV weak lensing surveys.
It is based on forward modelling and fast MCMC sampling.
To acknowledge this work, please cite the following paper: [Euclid Collaboration: G. Congedo et al., A&A 691, A319 (2024), arXiv:2405.00669](https://arxiv.org/abs/2405.00669).

Contact: <giuseppe.congedo@ed.ac.uk>

## Dependencies

LensMC is written for Python 3, please see [requirements.txt](requirements.txt).

## Install

### From the official repository (recommended)

Please use `pip` (see [PyPI project](https://pypi.org/project/lensmc)):
```bash
pip install lensmc
```
This will fetch a source distribution and build it locally. A source distribution is preferred over a pre-built binary wheel to prioritise runtime performance over build execution speed.

A local Python environment with the required dependencies can also be created beforehand by invoking:
```bash
make
```
Then, make sure the environment is sourced before calling `pip`:
```bash
source lensmc-env/bin/activate
```

### Via Makefile in a conda environment

Build environment and install LensMC:
```bash
make
make install
```

Source the environment:
```bash
source lensmc-env/bin/activate
python
Python 3.9.15 | packaged by conda-forge | (main, Nov 22 2022, 15:55:03) 
[GCC 10.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import lensmc
>>>
```

### Via setuptools

LensMC can also be installed into any environment with:
```bash
python setup.py install
```
Please use the `--user` option to install it in the user space, or source an environment beforehand (e.g. as in the previous section).

### From a source distribution

Assuming a LensMC environment is available, a source distribution can be made through:
```bash
make dist
```
The output tarball will be found in the `dist` directory. This can be distributed and then installed as follows:
```bash
pip install dist/lensmc*.tar.gz
```

## Documentation

[lensmc.readthedocs.io](https://lensmc.readthedocs.io/) (currently under construction and subject to change).

## License

GNU Lesser General Public License - Copyright (C) 2015 Giuseppe Congedo, University of Edinburgh on behalf of the Euclid Science Ground Segment
