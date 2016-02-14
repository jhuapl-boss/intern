# How to Build Docs

The `ndio` directory should have a sister directory `ndio-docs` at the same level, which is checked out to the `gh-pages` branch.

```
# from ndio directory:
sphinx-apidoc -o ../ndio-docs ./ndio/ -f -e
cd docs
make html
```
