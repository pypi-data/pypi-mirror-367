import os

try:
    from .measure_shear import measure_shear
    from .measure_shear_all import measure_shear_all
    # noinspection PyUnresolvedReferences
    from .linear_fit import linear_fit
except ModuleNotFoundError:
    raise ImportError('LensMC has not been installed yet.')


# fetch info from file
fname = os.path.join(os.path.dirname(__file__), 'INFO')
if os.path.isfile(fname):

    # read in file
    with open(fname, 'r') as fo:
        lines = fo.readlines()

    # parse contents to package attributes
    def get_var(key):
        ix = [lines.index(line) for line in lines if key in line][0]
        return lines[ix].strip().replace(f'{key}: ', '')

    __author__ = get_var('author')
    __email__ = get_var('email')
    __name__ = get_var('name')
    __description__ = get_var('description')
    __url__ = get_var('url')
    __version__ = get_var('version')
    __commit__ = get_var('commit')
    __license__ = get_var('license')

else:
    __author__ = __email__ = __name__ = __description__ = __url__ = __version__ = __status__ = __license__ = ''

# dereference variables
del fname, fo, lines, get_var
