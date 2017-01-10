"""
A Python library for open neuroscience data access and manipulation.
"""

version = "0.9.1"


def check_version():
    """
    Tells you if you have an old version of intern.
    """
    import requests
    r = requests.get('https://pypi.python.org/pypi/intern/json').json()
    r = r['info']['version']
    if r != version:
        print("A newer version of intern is available. " +
              "'pip install -U intern' to update.")
    return r
