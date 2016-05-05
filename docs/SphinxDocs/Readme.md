# Generating HTML Documentation

`$NDIO` is the location of the ndio repository.

```shell
cd $NDIO/docs/SphinxDocs

# Ensure Sphinx and the ReadTheDocs theme is available.
pip3 install -r requirements.txt

./makedocs.sh
```

Documentation will be placed in `$NDIO/docs/SphinxDocs/_build/html`.
