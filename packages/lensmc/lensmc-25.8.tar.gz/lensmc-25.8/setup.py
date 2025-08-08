"""
Lensmc - a Python package for weak lensing shear measurements.
Setup script.

Copyright 2015 Giuseppe Congedo
"""

import re
import os
from setuptools import setup, find_packages
from setuptools.extension import Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext
from datetime import datetime
from numpy import get_include
from subprocess import check_output, PIPE


# INFO filename
info_fname = 'lensmc/INFO'

# check existence: if so, read it in
if os.path.isfile(info_fname):

    # read from file
    with open(info_fname, 'r') as fo:
        lines = fo.readlines()

    # parse contents to package attributes
    def get_var(key):
        ix = [lines.index(line) for line in lines if key in line][0]
        return lines[ix].strip().replace(f'{key}: ', '')

    # set attributes
    __author__ = get_var('author')
    __email__ = get_var('email')
    __name__ = get_var('name')
    __description__ = get_var('description')
    __url__ = get_var('url')
    __version__ = get_var('version')
    __license__ = get_var('license')

else:

    # define attributes
    __author__ = 'Giuseppe Congedo'
    __email__ = 'giuseppe.congedo@ed.ac.uk'
    __name__ = 'lensmc'
    __description__ = 'Python package for weak lensing shear measurements'
    __url__ = 'https://gitlab.com/lensmc/LensMC'
    try:
        commit = check_output(['git', 'rev-parse', '--short', 'HEAD'], stderr=PIPE).strip().decode('utf-8')
        timestamp = int(check_output(['git', 'show', '-s', '--format=%ct', commit], stderr=PIPE).strip().decode('utf-8'))
        year_month = datetime.fromtimestamp(timestamp).strftime('%y.%-m')
    except Exception as e:
        print(e)
        commit = ''
        year_month = datetime.today().strftime("%y.%-m")
    ver = os.getenv('VERSION')
    if ver:
        __version__ = ver
    else:
        __version__ = f'{year_month}'
    __commit__ = commit
    __license__ = 'LGPL - Copyright (C) 2015 Giuseppe Congedo, University of Edinburgh on behalf of the Euclid Science Ground Segment'

    # save to file
    with open(info_fname, 'w') as fo:
        fo.write(f'author: {__author__}\n')
        fo.write(f'email: {__email__}\n')
        fo.write(f'name: {__name__}\n')
        fo.write(f'description: {__description__}\n')
        fo.write(f'url: {__url__}\n')
        fo.write(f'version: {__version__}\n')
        fo.write(f'commit: {__commit__}\n')
        fo.write(f'license: {__license__}\n')


def get_version(package, text, ftype='requirements'):
    match_str = '.=.*?\n'
    res = re.search(f'{package}{match_str}', text)
    if res:
        return res[0].split('\n')[0]
    else:
        raise Exception(f'Package {package} not found in {text}. Please double check format.')


# get Python version from Makefile
with open('environment.yml', 'r') as fo:
    python_ver = re.findall('\d.\d', get_version('python', fo.read()).split('=')[-1])[0]

# get Python packages versions from requirements.txt
with open('requirements.txt', 'r') as fo:
    requirements = fo.read()

    install_requires = [get_version('numpy', requirements),
                        get_version('scipy', requirements),
                        get_version('astropy', requirements),
                        get_version('pyfftw', requirements)]

data_files = [f'{__name__}/INFO',
              f'{__name__}/aux/cache_1x.bin', f'{__name__}/aux/cache_3x.bin',
              f'{__name__}/aux/cache_5x.bin', f'{__name__}/aux/cache_7x.bin',
              f'{__name__}/aux/se++.config', f'{__name__}/aux/seg_filter.conv',
              f'{__name__}/aux/se.config', f'{__name__}/aux/se.param',
              f'{__name__}/aux/swarp.config',
              'requirements.txt', 'environment.yml']

# external modules
ext_modules = [
    Extension(
        name=f'{__name__}.galaxy_model',
        sources=[f'{__name__}/src/cython/galaxy_model.pyx',
                 f'{__name__}/src/c/fast_fourier_model.cpp'],
        include_dirs=[get_include(), f'{__name__}/src/c'],
        language='c++',
        extra_compile_args=['-Ofast', '-fpic']
        ),
    Extension(
        name=f'{__name__}.star_model',
        sources=[f'{__name__}/src/cython/star_model.pyx',
                 f'{__name__}/src/c/fast_fourier_model.cpp'],
        include_dirs=[get_include(), f'{__name__}/src/c'],
        language='c++',
        extra_compile_args=['-Ofast', '-fpic'],
        ),
    Extension(
        name=f'{__name__}.cross_product',
        sources=[f'{__name__}/src/cython/cross_product.pyx'],
        include_dirs=[get_include()],
        language='c',
        extra_compile_args=['-Ofast', '-fpic']
        ),
    Extension(
        name=f'{__name__}.linear_fit',
        sources=[f'{__name__}/src/cython/linear_fit.pyx'],
        include_dirs=[get_include()],
        language='c',
        extra_compile_args=['-Ofast', '-fpic']
    )
]

# installation
setup(
    name=__name__,
    version=__version__,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Operating System :: POSIX :: Linux',
        f'Programming Language :: Python :: {python_ver}',
        'Programming Language :: C++',
        'Topic :: Scientific/Engineering :: Astronomy',
        ],
    description=__description__,
    url=__url__,
    author=__author__,
    author_email=__email__,
    long_description=open('docs/description.md').read(),
    long_description_content_type='text/markdown',
    license=__license__,
    packages=find_packages(),
    data_files=[('.', data_files)],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    cmdclass={'build_ext': build_ext},
    ext_modules=cythonize(ext_modules, language_level=3),
)
