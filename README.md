# intern

[![PyPI version](https://badge.fury.io/py/intern.svg)](https://badge.fury.io/py/intern)
[![CircleCI](https://circleci.com/gh/jhuapl-boss/intern.svg?style=svg)](https://circleci.com/gh/jhuapl-boss/intern)

**intern** (Integrated Toolkit for Extensible and Reproducible Neuroscience) is
a Python 2/3 module that enables big-data neuroscience. Currently, it provides
an interface to the Boss API, and in the future may provide interfaces to other
neuroscience databases.

intern is inspired by the [NeuroData](http://neurodata.io) ndio package:

[https://github.com/neurodata/ndio](https://github.com/neurodata/ndio)

## The Boss Legal Notes

Use or redistribution of the Boss system in source and/or binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code or binary forms must adhere to the terms and conditions of any applicable software licenses.
2. End-user documentation or notices, whether included as part of a redistribution or disseminated as part of a legal or scientific disclosure (e.g. publication) or advertisement, must include the following acknowledgement: The Boss software system was designed and developed by the Johns Hopkins University Applied Physics Laboratory (JHU/APL).
3. The names "The Boss", "JHU/APL", "Johns Hopkins University", "Applied Physics Laboratory", "MICrONS", or "IARPA" must not be used to endorse or promote products derived from this software without prior written permission. For written permission, please contact BossAdmin@jhuapl.edu.
4. This source code and library is distributed in the hope that it will be useful, but is provided without any warranty of any kind.

## Installation

-   It's always a good idea to use virtualenv to isolate your work from your system Python installation

        	- Using [virtualenv](https://virtualenv.pypa.io/en/stable/):

        	```
        	virtualenv intern
        	. intern/bin/activate
        	```

        	- Using [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/):

        	```
        	mkvirtualenv intern
        	```

-   (Preferred) Install via pypi

        	```
        	pip install intern
        	```

-   Install via git

    Clone the repository from https://github.com/jhuapl-boss/intern and run
    `pip install -r requirements.txt` from the repository's location on your
    system.

    Add `<repository location>` to your `PYTHONPATH`.

    For example, on a \*nix system, if intern was cloned to ~/intern:

    `export PYTHONPATH=$PYTHONPATH:~/intern`

For Python 2 support, you will need to install intern v0.10.0 or earlier.

## Getting Started

To quickly get started with intern, check out the wiki: [https://github.com/jhuapl-boss/intern/wiki](https://github.com/jhuapl-boss/intern/wiki)

## Documentation

Full detailed documentation can be found here: [https://jhuapl-boss.github.io/intern/](https://jhuapl-boss.github.io/intern/)

## Contributing

Please submit bug reports, or get in touch using GitHub Issues.
