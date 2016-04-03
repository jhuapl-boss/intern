from __future__ import absolute_import
import six
from six.moves import range
from six.moves import zip


class InvalidEnumerationException(Exception):
    def __init__(self, msg="Invalid Enumeration."):
        self.msg = msg

    def __str__(self):
        return self.msg


def enum(*sequential, **named):
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
