
class InvalidRAMONError(Exception):
    """
    Raised when an invalid RAMON object is referenced or created.
    """
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg
