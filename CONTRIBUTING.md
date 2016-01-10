# Contributing

## Getting Started
- Start by navigating to https://github.com/openconnectome/ndio and forking the project to your own GitHub account.

  ```
  git clone https://github.com/openconnectome/ndio.git
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
- Make your changes and push to your fork. Then, take out a pull-request against the master branch of the official openconnectome/ndio repository. Be sure your code subscribes to our style guide (below)!

# Style Guide
We adhere to the [Google Style Guide](https://google.github.io/styleguide/pyguide.html) whenever possible, and use the Google docstring styleguide as well. Optional arguments can be 'defaulted' with the syntax: `param_name (type: Default): Description`.

For instance:

```
    answer (int: 42): The universal answer to supply to the function
```
