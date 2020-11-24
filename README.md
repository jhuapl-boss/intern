# intern

[![PyPI version](https://badge.fury.io/py/intern.svg)](https://badge.fury.io/py/intern)
![Python 3.6/3.7 Tests](https://github.com/jhuapl-boss/intern/workflows/Test%20Python%20Package/badge.svg?branch=master&event=push)

**intern** (Integrated Toolkit for Extensible and Reproducible Neuroscience) is
a Python 2/3 module that enables big-data neuroscience. Currently, it provides
an interface to the Boss API, and in the future may provide interfaces to other
neuroscience databases.

## The Boss Legal Notes

Use or redistribution of the Boss system in source and/or binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code or binary forms must adhere to the terms and conditions of any applicable software licenses.
2. End-user documentation or notices, whether included as part of a redistribution or disseminated as part of a legal or scientific disclosure (e.g. publication) or advertisement, must include the following acknowledgement: The Boss software system was designed and developed by the Johns Hopkins University Applied Physics Laboratory (JHU/APL).
3. The names "The Boss", "JHU/APL", "Johns Hopkins University", "Applied Physics Laboratory", "MICrONS", or "IARPA" must not be used to endorse or promote products derived from this software without prior written permission. For written permission, please contact BossAdmin@jhuapl.edu.
4. This source code and library is distributed in the hope that it will be useful, but is provided without any warranty of any kind.

## Installation

-   It's always a good idea to use virtualenv to isolate your work from your system Python installation:

-   Using [virtualenv](https://virtualenv.pypa.io/en/stable/):

```shell
virtualenv intern
. intern/bin/activate
```

-   Using [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/):

```shell
mkvirtualenv intern
```

-   (Preferred) Install via pypi

```shell
pip install intern
```

-   Install via git

Clone the repository from https://github.com/jhuapl-boss/intern and run
`pip install -r requirements.txt` from the repository's location on your
system.

Add `<repository location>` to your `PYTHONPATH`.

For example, on a \*nix system, if intern was cloned to ~/intern:

`export PYTHONPATH=$PYTHONPATH:~/intern`

> **For Python 2 support, you will need to install intern v0.10.0 or earlier.**

### Optional Dependencies
To install depedencies required to use the [cloud-volume](https://github.com/seung-lab/cloud-volume) remote, run the command: 

```shell
pip install intern[cloudvolume]
```

## Getting Started

To quickly get started with intern, check out the wiki: [https://github.com/jhuapl-boss/intern/wiki](https://github.com/jhuapl-boss/intern/wiki)

## Documentation

Full detailed documentation can be found here: [https://jhuapl-boss.github.io/intern/](https://jhuapl-boss.github.io/intern/)

## Contributing

Please submit bug reports, or get in touch using GitHub Issues.

## Citation

If you find this library useful to your work, please consider citing the following:

https://www.biorxiv.org/content/10.1101/2020.05.15.098707v1

```
@article{intern,
	doi = {10.1101/2020.05.15.098707},
	url = {https://www.biorxiv.org/content/10.1101/2020.05.15.098707v1},
	year = 2020,
	month = {may},
	publisher = {BiorXiv},
	author = {Matelsky, Jordan K and Rodriguez, Luis and Xenes, Daniel and Gion, Timothy and Hider Jr., Robert and Wester, Brock and Gray-Roncal, William},
	title = {{intern: Integrated Toolkit for Extensible and Reproducible Neuroscience}},
	journal = {BiorXiv}
}
```
