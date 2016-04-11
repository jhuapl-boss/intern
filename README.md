# ndio

[![](https://img.shields.io/pypi/v/ndio.svg)](https://pypi.python.org/pypi/ndio)
[![Build Status](https://travis-ci.org/neurodata/ndio.svg?branch=master)](https://travis-ci.org/neurodata/ndio)
[![Code Climate](https://codeclimate.com/github/neurodata/ndio/badges/gpa.svg)](https://codeclimate.com/github/neurodata/ndio)


**ndio** is a Python 2 and 3 module that enables big-data neuroscience, as well as direct interfacing with NeuroData workflows and servers. More complete documentation is available at [the ndio documentation website](http://docs.neurodata.io/nddocs/ndio).

ndio is now considered stable as of the 1.0 release in April 2016.

## Installation

Before you install ndio, you'll need to have a few prerequisites. The first thing to do is to **install numpy**, which often does not jive well with the auto-installation process supported by `pip`.

If you already have numpy installed, then simply run:

```
pip install ndio
```

Generally, installation failures can be fixed by running the same line again, which, yeah, that's super janky, whatever. If that still fails, try cloning the repository from https://github.com/neurodata/ndio and running `pip install -r requirements.txt`.

If you're still having no luck, try checking out the `travis.yml` file in the main directory of the repository — these are the lines required to get ndio up and running on a totally blank Ubuntu 14.04 machine.

## Getting Started

You can view a list of not-necessarily-too-up-to-date tutorials, and some information about getting started,
over [here](<http://docs.neurodata.io/nddocs/ndio/tutorials.html>).

## Contributing

Please submit bug reports, or get in touch at our [GitHub
repository](<https://github.com/neurodata/ndio>). When contributing, please
follow the [Contribution
Guidelines](<https://github.com/neurodata/ndio/blob/master/CONTRIBUTING.md>).

## Documentation

ndio is fully documented [here](<http://docs.neurodata.io/ndio/>).

Submit bug reports [here](<https://github.com/neurodata/ndio/issues/new>).
