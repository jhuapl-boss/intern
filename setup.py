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
    version = '0.0.1',
    description = 'A Python library for neuroscience data access and manipulation.',
    author = 'Jordan Matelsky',
    author_email = 'j6k4m8@gmail.com',
    url = 'https://github.com/openconnectome/ndio',
    download_url = 'https://github.com/openconnectome/ndio/tarball/0.0.1',
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
