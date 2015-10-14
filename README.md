# ndio
A Python interface to neurodata.

[![](https://img.shields.io/pypi/dm/ndio.svg)](https://pypi.python.org/pypi/ndio)
[![](https://img.shields.io/pypi/v/ndio.svg)](https://pypi.python.org/pypi/ndio)
[![](https://img.shields.io/badge/SfN-2015-blue.svg)](http://www.sfn.org/annual-meeting/neuroscience-2015)

Submit bug reports [here](https://github.com/openconnectome/ndio/issues/new).

## Changelog

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
- [x] Begin test suite
