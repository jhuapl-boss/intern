from setuptools import setup, find_packages
from codecs import open
from os import path
from intern import __version__

# to update
# python setup.py sdist
# twine upload dist/*


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# get the dependencies and installs
with open(path.join(here, "requirements.txt"), encoding="utf-8") as f:
    all_reqs = f.read().split("\n")

install_requires = [x.strip() for x in all_reqs if "git+" not in x]
dependency_links = [
    x.strip().replace("git+", "") for x in all_reqs if x.startswith("git+")
]

setup(
    name="intern",
    version=__version__,
    description="Python SDK for interacting with neuroscience data via the Boss API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jhuapl-boss/intern",
    download_url="https://github.com/jhuapl-boss/intern/tarball/" + __version__,
    license="Apache 2.0",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    keywords=[
        "brain",
        "microscopy",
        "neuroscience",
        "connectome",
        "connectomics",
        "spatial",
        "EM",
        "electron",
        "calcium",
        "database",
        "boss",
        "microns",
    ],
    packages=find_packages(exclude=["docs", "tests*"]),
    include_package_data=True,
    author="Johns Hopkins University Applied Physics Laboratory",
    install_requires=install_requires,
    dependency_links=dependency_links,
    author_email="iarpamicrons@jhuapl.edu",
)
