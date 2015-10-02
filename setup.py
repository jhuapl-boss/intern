VERSION = '0.0.3'
"""
roll with
git tag VERSION
git push --tags
python setup.py sdist upload -r pypi
"""

from distutils.core import setup
setup(
    name = 'ndio',
    packages = [
        'ndio',
        'ndio.convert',
        'ndio.ramon',
        'ndio.remote',
        'ndio.utils'
    ],
    version = VERSION,
    description = 'A Python library for neuroscience data access and manipulation.',
    author = 'Jordan Matelsky',
    author_email = 'j6k4m8@gmail.com',
    url = 'https://github.com/openconnectome/ndio',
    download_url = 'https://github.com/openconnectome/ndio/tarball/' + VERSION,
    keywords = [
        'brain',
        'neuro',
        'neurodata',
        'neurodata.io',
        'neuroscience',
        'ocpy',
        'ocp',
        'ocp.me',
        'connectome',
        'connectomics'
    ],
    classifiers = [],
)
