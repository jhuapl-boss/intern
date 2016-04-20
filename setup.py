import ndio
from distutils.core import setup

VERSION = ndio.version
"""
update docs with the `generatedocs` script.

roll with:

git tag VERSION
git push --tags
python setup.py sdist upload -r pypi
"""

setup(
    name='ndio',
    packages=[
        'ndio',
        'ndio.convert',
        'ndio.ramon',
        'ndio.remote',
        'ndio.utils'
    ],
    version=VERSION,
    description='A Python library for open neuroscience data access and \
manipulation.',
    author='Jordan Matelsky',
    author_email='jordan@neurodata.io',
    url='https://github.com/neurodata/ndio',
    download_url='https://github.com/neurodata/ndio/tarball/' + VERSION,
    keywords=[
        'brain',
        'medicine',
        'microscopy',
        'neuro',
        'neurodata',
        'neurodata.io',
        'neuroscience',
        'ndio',
        'ocpy',
        'ocp',
        'ocp.me',
        'connectome',
        'connectomics',
        'spatial',
        'EM',
        'MRI',
        'fMRI',
        'calcium'
    ],
    classifiers=[],
    setup_requires=[
        "requests",
        'numpy',
    ],
    install_requires=[
        "pillow>=3.2.0",
        "numpy>=1.0.0",
        "h5py>=2.6.0",
        "requests",
        "blosc>=1.3.0",
        "jsonschema",
        "json-spec"
    ]
)
