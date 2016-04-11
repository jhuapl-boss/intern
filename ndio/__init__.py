version = "1.0.0"


def check_version():
    """
    Tells you if you have an old version of ndio.
    """
    import requests
    r = requests.get('https://pypi.python.org/pypi/ndio/json').json()
    r = r['info']['version']
    if r != version:
        print("A newer version of ndio is available. " +
              "'pip install -U ndio' to update.")
    return r
