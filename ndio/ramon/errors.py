
class InvalidRAMONError(Exception):
    """
    Raised when an invalid RAMON object is referenced or created.
    """

    def __init__(self, msg):
        """
        Initialize the error.
        """
        self.msg = msg

    def __str__(self):
        """
        String parser for the casted representation.
        """
        return self.msg
