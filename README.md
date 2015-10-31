# ndio
A Python interface to neurodata.

[![](https://img.shields.io/pypi/dm/ndio.svg)](https://pypi.python.org/pypi/ndio)
[![](https://img.shields.io/pypi/v/ndio.svg)](https://pypi.python.org/pypi/ndio)
[![](https://img.shields.io/badge/SfN-2015-blue.svg)](http://www.sfn.org/annual-meeting/neuroscience-2015)

Submit bug reports [here](https://github.com/openconnectome/ndio/issues/new).

## Changelog

- **0.0.16** (October 31 2015)
    - RAMON Downloads
    - HDF5-to-RAMON conversion
- **0.0.15**
    - Bug fixes
- **0.0.14** (October 29 2015)
    - Remove excess code for RAMON downloads
    - Fix some old docstrings so everything's pretty again
    - Add channel addition and removal
    - Add IMAGE and ANNOTATION enumerables
- **0.0.13** (October 26 2015)
    - RAMON Downloads fully working for `Segments`
    - OCPMeta Remote support for `set`s with `secret`
- **0.0.12** (October 19 2015)
    - OCP Metadata Access
    - Add API key support to coincide with new API keys on LIMS server
    - Fix png export behavior
- **0.0.11** (October 18 2015)
    - A few more bug fixes in time for SfN
- **0.0.10** (October 17 2015)
    - Bug fixes for volume uploads
- **0.0.9** (October 17 2015)
    - OCPMeta for get/set by token
    - Fixes for URL construction
- **0.0.8** (October 13 2015)
    - RAMONSegment downloads
    - Begin test suite
- **0.0.7** (October 11 2015)
    - Download RAMON metadata (thanks Alex!)
    - OCPMeta Remote
- **0.0.6** (October 9 2015)
    - `post_cutout` to upload cutout data to writeable projects
    - A bunch of better error handling
    - Prepping for more `Remote`s eventually
- **0.0.5** (October 7 2015)
    - `ndio.version` attribute, plus better version management
    - Allows writing image files directly from binary string
    - Optimized download code for numpy-array access

## Under Development
- [ ] Upload RAMON
- [ ] Download RAMON objects
