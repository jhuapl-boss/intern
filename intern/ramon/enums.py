from __future__ import absolute_import
import six
from six.moves import range
from six.moves import zip


class InvalidEnumerationException(Exception):
    """
    An exception that is thrown when an invalid enumeration is used.
    This is deprecated.
    """

    def __init__(self, msg="Invalid Enumeration."):
        """
        Initialize the invalid-enum error.
        """
        self.msg = msg

    def __str__(self):
        """
        String representation of the InvalidEnumerationException
        """
        return self.msg


def enum(*sequential, **named):
    """
    A helper function to make enums in Python 2.
    """
    enums = dict(list(zip(sequential, list(range(len(sequential))))), **named)
    reverse = dict((value, key) for key, value in six.iteritems(enums))
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)

eRAMONAnnoStatus = enum("DEFAULT",
                        UNPROCESSED=0,
                        LOCKED=1,
                        PROCESSED=2,
                        IGNORED=3)

DEFAULT_ID = 0
DEFAULT_CONFIDENCE = 0
DEFAULT_DYNAMIC_METADATA = {}
DEFAULT_STATUS = eRAMONAnnoStatus.DEFAULT
DEFAULT_AUTHOR = ''
