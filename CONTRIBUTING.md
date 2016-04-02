# Contributing

## Getting Started
- Start by navigating to https://github.com/neurodata/ndio and forking the project to your own GitHub account.

  ```
  git clone https://github.com/neurodata/ndio.git
  ```
- Download the required packages. This can be done easily with pip:

  ```
  pip install -r requirements.txt
  ```
- Ensure that the test suite runs (if it's running successfully on the CI server! Otherwise, all bets are off...) by running:

  ```
  coverage run -m unittest discover
  ```

## Contributing Code
It is highly recommended that you reach out to the development team at ndio@neurodata.io before beginning on a project, as it may already be under development.

- Check out a new branch on your forked copy of the repo. By convention, we prefix branch names with `add-` if it's a feature addition, `fix-` if it's a bug-fix, etc.

  ```
  git checkout -b add-json-exports
  ```
- Make your changes and push to your fork. Then, take out a pull-request against the master branch of the official neurodata/ndio repository. Be sure your code subscribes to our style guide (below)!

# Style Guide
We adhere to the [Google Style Guide](https://google.github.io/styleguide/pyguide.html) whenever possible, and use the Google docstring styleguide as well. Optional arguments can be 'defaulted' with the syntax: `param_name (type: Default): Description`.

For instance:

```
    answer (int: 42): The universal answer to supply to the function
```

## Code Conventions

- **Raise exceptions, don't print.**
  Raising exceptions sends  output to `stderr`, which is good — printing goes to `stdout`. Consider the following script:

  ```
  # print_csv.py
  import ndio.remote.neurodata as ND
  import sys
  
  nd = ND()
  
  print ",".join([i for i in nd.get_ramon_ids(sys.argv[1], sys.argv[2])])
  ```
  
  This script accepts two command-line arguments and prints out a CSV of token/channel IDs:
  
  ```
  python print_csv.py kasthuri2015_ramon_v1 neurons > out.csv
  ```
  
  If you print warnings, you'll ruin the CSV schema!
  
- **Double-quotes unless you need double-quotes inside the quotes. Then, single quotes.**

### Naming

Because we anticipate users aliasing packages when they're imported instead of `import`ing `*` from a package, we can use that to our advantage and make our function names shorter. For instance:

```
import ndio.convert.png as png

png.from_cutout( . . . )
```

Conventions are as follows:

- Converters or exporters should be titled `from_{fmt}` or `to_{fmt}`, and their package predicate should elaborate on the source or target format. For instance, `ramon.to_hdf5()` quite clearly converts *from* RAMON *to* hdf5.
- Filenames come first, then data. (Keeping with common python package tradition.)
