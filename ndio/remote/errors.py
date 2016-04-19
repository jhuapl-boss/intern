
class RemoteError(Exception):
    """
    A generic error arising from an issue pertaining
    to ndio Remotes.
    """

    def __init__(self, message):
        """
        Initialize the error.
        """
        super(Exception, self).__init__(message)


class RemoteDataNotFoundError(RemoteError):
    """
    Called when data is requested from a Remote but the
    server either cannot access it (maybe a permissions issue?)
    or the data does not exist.
    """

    def __init__(self, message):
        """
        Initialize the error.
        """
        super(RemoteError, self).__init__(message)


class RemoteDataUploadError(RemoteError):
    """
    Called when there's an issue during data upload. Could be
    because you don't have write access to this channel, or
    because there's a problem with your data. (Check your bounds?)
    """

    def __init__(self, message):
        """
        Initialize the error.
        """
        super(RemoteError, self).__init__(message)


class BadAPIKeyError(RemoteError):
    """
    Called when you do not specify an API key and one is needed,
    or if you specify an API key that does not match the requirements
    to access/edit the data you're accessing/editing.
    """

    def __init__(self, message):
        """
        Initialize the error.
        """
        super(RemoteError, self).__init__(message)
