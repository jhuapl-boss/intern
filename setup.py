from setuptools import setup, find_packages
from codecs import open
from os import path

__version__ = '0.9.0'

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# get the dependencies and installs
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if x.startswith('git+')]

setup(
    name='intern',
    version=__version__,
    description='Python SDK for the Boss API - neuroscience data.',
    long_description=long_description,
    url='https://github.com/jhuapl-boss/intern',
    download_url='https://github.com/jhuapl-boss/intern/tarball/' + __version__,
    license='Apache 2.0',
    classifiers=[
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'Programming Language :: Python :: 3.4',
      'Programming Language :: Python :: 3.5',
      'Programming Language :: Python :: 2.7',
    ],
    keywords='neuroscience database sdk microns boss',
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    author='Johns Hopkins University Applied Physics Laboratory',
    install_requires=install_requires,
    dependency_links=dependency_links,
    author_email='iarpamicrons@jhuapl.edu'
)
